from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module
from generator import Generator
from secrets import Secrets

class TestSecrets(unittest.TestCase):

    def setUp(self):
        self.cfg = config_module.config
        self.secrets = Secrets(self.cfg)
        self.generator = Generator(self.cfg)
        self.candidates=  ["alpha", "bravo", "charl","alexa"]

    def test_initialization(self):
        self.assertEqual(self.secrets.words_path, self.cfg.secrets_file)
        self.assertIsNotNone(self.secrets.random)

    def test_get_secrets(self):
        self.cfg.secrets_file.write_text("\n".join(self.candidates))
        result = self.secrets.get_secrets()
        self.assertEqual(result, self.candidates)

    def test_get_secret_returns_valid_entry(self):
        self.cfg.secrets_file.write_text("\n".join(self.candidates))    
        chosen = self.secrets.get_secret()
        self.assertIn(chosen, self.candidates)

    def test_write_secret(self):
        self.secrets.write_secret("first")
        current=self.secrets.get_secrets()
        self.assertIn("first", current)

    def test_load_secret(self):
        self.secrets.load_secret(self.generator)
        stored = self.secrets.get_secrets()
        length=len(stored)
        self.assertEqual(length, self.cfg.word_count)
        for word in stored:
            self.assertEqual(len(word), self.cfg.word_length)

    def test_clear_secrets(self):
        self.cfg.secrets_file.write_text("\n".join(self.candidates))
        self.secrets.clear_secrets()
        print(self.secrets.words_path.exists())
        print(self.secrets.count_secrets())
        self.assertEqual(self.secrets.count_secrets(), 0)
        self.assertFalse(self.secrets.words_path.exists())

if __name__ == "__main__":
    unittest.main()