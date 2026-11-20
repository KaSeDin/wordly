from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module
from secrets import Secrets


class TestSecretsWithRealConfig(unittest.TestCase):
    """Unit tests for Secrets backed by the real Config and an isolated temporary secrets file."""

    def setUp(self) -> None:
        """Clone the real Config with a temporary secrets file path for each test."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        temp_secrets_path = Path(self.tmp_dir.name) / "test_secrets.txt"

        # Uses actual Config values (word_length, word_count, max_guesses, etc.)
        # while isolating file writes to a temporary file.
        self.cfg = replace(config_module.config, secrets_file=temp_secrets_path)
        self.secrets = Secrets(self.cfg)
        self.candidates = ["alpha", "bravo", "charlie", "delta"]

    def tearDown(self) -> None:
        """Remove the temporary directory and any test files created during the test."""
        self.tmp_dir.cleanup()

    def test_initialization_uses_config(self):
        """Verify Secrets resolves words_path from cfg.secrets_file and initializes dependencies."""
        self.assertEqual(self.secrets.words_path, self.cfg.secrets_file)
        self.assertIsNotNone(self.secrets.random)
        self.assertIsNotNone(self.secrets.generator)
        self.assertEqual(self.secrets.generator.cfg, self.cfg)
        self.assertEqual(str(self.secrets), f"Secrets(words_path={self.cfg.secrets_file})")

    def test_get_secrets_empty_when_file_missing(self):
        """Verify get_secrets() returns an empty list when the secrets file does not exist yet."""
        self.assertEqual(self.secrets.get_secrets(), [])
        self.assertEqual(self.secrets.count_secrets(), 0)

    def test_get_secrets_reads_existing_entries(self):
        """Verify get_secrets() reads all non-empty lines from the secrets file."""
        self.cfg.secrets_file.write_text("\n".join(self.candidates) + "\n", encoding="utf-8")

        result = self.secrets.get_secrets()
        self.assertEqual(result, self.candidates)
        self.assertEqual(self.secrets.count_secrets(), len(self.candidates))

    def test_get_secret_returns_valid_entry(self):
        """Verify get_secret() picks a word present in the stored secrets."""
        self.cfg.secrets_file.write_text("\n".join(self.candidates) + "\n", encoding="utf-8")

        chosen = self.secrets.get_secret()
        self.assertIn(chosen, self.candidates)

    def test_get_secret_raises_when_no_secrets_exist(self):
        """Verify get_secret() raises ValueError when no secrets are available."""
        with self.assertRaises(ValueError):
            self.secrets.get_secret()

    def test_write_secret_appends_and_normalizes(self):
        """Verify write_secret() normalizes casing/whitespace and persists the word."""
        self.secrets.write_secret("  First  ")
        self.secrets.write_secret("SECOND")

        current = self.secrets.get_secrets()
        self.assertEqual(current, ["first", "second"])

    def test_load_secret_adds_one_word_matching_config_length(self):
        """Verify load_secret() generates and appends one secret word of cfg.word_length."""
        self.secrets.load_secret()

        stored = self.secrets.get_secrets()
        self.assertEqual(len(stored), 1)
        self.assertEqual(len(stored[0]), self.cfg.word_length)
        self.assertEqual(stored[0], stored[0].lower())

    def test_load_secrets_adds_word_count_words_matching_config_length(self):
        """Verify load_secrets() appends cfg.word_count words matching cfg.word_length."""
        self.secrets.load_secrets()

        stored = self.secrets.get_secrets()
        self.assertEqual(len(stored), self.cfg.word_count)
        for word in stored:
            self.assertEqual(len(word), self.cfg.word_length)
            self.assertEqual(word, word.lower())

    def test_clear_secrets_deletes_file_and_resets_count(self):
        """Verify clear_secrets() removes the secrets file and brings count back to zero."""
        self.cfg.secrets_file.write_text("\n".join(self.candidates) + "\n", encoding="utf-8")
        self.assertTrue(self.secrets.words_path.exists())

        self.secrets.clear_secrets()

        self.assertFalse(self.secrets.words_path.exists())
        self.assertEqual(self.secrets.count_secrets(), 0)


if __name__ == "__main__":
    unittest.main()