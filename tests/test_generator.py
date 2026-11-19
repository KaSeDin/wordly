from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config
from generator import Generator

class TestGenerator(unittest.TestCase):

    def setUp(self):
        self.cfg=config.config
        self.gen=Generator(self.cfg)

    def test_initialization_sets_attributes(self):
        self.assertEqual(self.gen.size, self.cfg.word_length)
        self.assertEqual(self.gen.word_count, self.cfg.word_count)
        self.assertIsNotNone(self.gen.rw)

    def test_get_word_returns_string_of_expected_size_without_spaces(self):
        word = self.gen.getWord()

        self.assertIsInstance(word, str)
        self.assertEqual(len(word), self.gen.size)
        self.assertNotIn(" ", word)
        self.assertEqual(word, word.lower())

    def test_get_words_returns_expected_count_and_each_word_size(self):
        words = self.gen.getWords()

        self.assertIsInstance(words, list)
        self.assertEqual(len(words), self.gen.word_count)
        for word in words:
            self.assertIsInstance(word, str)
            self.assertEqual(len(word), self.gen.size)
            self.assertNotIn(" ", word)
            self.assertEqual(word, word.lower())

if __name__ == "__main__":
    unittest.main()