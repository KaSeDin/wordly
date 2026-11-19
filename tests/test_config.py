from pathlib import Path 
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

class TestConfig(unittest.TestCase):
    
    def test_module_config_exists_and_is_config_instance(self):
        self.assertTrue(hasattr(config, "config"))
        self.assertIsInstance(config.config, config.Config)

    def test_load_config_returns_populated_config(self):
        cfg = config.load_config()
        self.assertIsInstance(cfg, config.Config)
        self.assertIsNotNone(cfg.secrets_file)
        self.assertIsNotNone(cfg.word_length)
        self.assertIsNotNone(cfg.word_count)

    def test_config_field_types_and_values_present(self):
        cfg = config.config

        self.assertIsInstance(cfg.secrets_file, Path)
        self.assertTrue(str(cfg.secrets_file).strip())

        self.assertIsInstance(cfg.word_length, int)
        self.assertGreater(cfg.word_length, 4)

        self.assertIsInstance(cfg.word_count, int)
        self.assertGreater(cfg.word_count, 2)

    def test_config_is_frozen(self):
        with self.assertRaises(AttributeError):
            config.config.word_length = config.config.word_length + 1

if __name__=="__main__":
    unittest.main()