from pathlib import Path
import sys
import unittest
from config import load_config
from generator import Generator

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestGenerator(unittest.TestCase):
    """Integration/unit tests for Generator using the actual loaded Config."""

    def setUp(self):
        """Load the actual config instance and initialize Generator from it."""
        self.cfg=load_config()
        self.gen=Generator.from_config(self.cfg)

    def _assert_strict_word_format(self, word: str) -> None:
        """Assert word is a non-empty, stripped, lowercase string of exact expected length."""
        self.assertIsInstance(word, str)
        self.assertTrue(word, "Generated word must not be empty.")
        self.assertEqual(word, word.strip(), "Generated word must not have leading/trailing whitespace.")
        self.assertNotIn(" ", word, "Generated word must not contain spaces.")
        self.assertEqual(word, word.lower(), "Generated word must be strictly lowercase.")
        self.assertEqual(
            len(word),
            self.cfg.word_length,
            f"Expected word length {self.cfg.word_length} from config, got {len(word)} for {word!r}.",
        )

    def test_initialization_matches_config(self):
        """Verify Generator attributes and string output match the loaded config."""
        self.assertIsInstance(self.gen, Generator)
        self.assertEqual(self.gen.size, self.cfg.word_length)
        self.assertEqual(self.gen.word_count, self.cfg.word_count)
        self.assertIsNotNone(self.gen.rw)
        self.assertEqual(
            str(self.gen),
            f"Generator(size={self.cfg.word_length}, word_count={self.cfg.word_count})",
        )

    def test_get_word_matches_config_size_and_strict_lowercase(self):
        """Verify getWord() returns a single strictly formatted word matching cfg.word_length."""
        word = self.gen.getWord()
        self._assert_strict_word_format(word)

    def test_get_words_matches_config_count_and_strict_format(self):
        """Verify getWords() returns cfg.word_count words, each matching cfg.word_length and lowercase."""
        words = self.gen.getWords()

        self.assertIsInstance(words, list)
        self.assertEqual(len(words), self.cfg.word_count)

        for word in words:
            self._assert_strict_word_format(word)

if __name__ == "__main__":
    unittest.main()