from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from guessresult import GuessResult
from outcome import Outcome
from state import State


class TestGuessResult(unittest.TestCase):

    def setUp(self):
        self.secret = "crane"
        self.bad_words = ["plant", "bongo", "brick", "flint", "gloom"]

    def test_exact_match_sets_matched_state_and_all_correct(self):
        result = GuessResult(self.secret, self.secret)
        self.assertIs(result.state, State.MATCHED)
        self.assertEqual(len(result.outcomes), len(self.secret))

    def _palindrome(self)->str:
        return self.secret[::-1]

    def test_misplaced_match_sets(self):
        result = GuessResult(self._palindrome(), self.secret)
        self.assertIs(result.state, State.UNMATCHED)
        self.assertEqual(len(result.outcomes), len(self.secret))
    
    def test_bad_word_batch_stays_unmatched(self):
        for word in self.bad_words:
            with self.subTest(word=word):
                result = GuessResult(word, self.secret)
                self.assertIs(result.state, State.UNMATCHED)
                self.assertEqual(len(result.outcomes), len(self.secret))
                self.assertNotEqual(
                    result.outcomes,
                    [Outcome.CORRECT] * len(self.secret),
                )


if __name__ == "__main__":
    unittest.main()