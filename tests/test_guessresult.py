from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from guessresult import GuessResult
from outcome import Outcome
from temp.state import State


class TestGuessResult(unittest.TestCase):
    """Unit tests for GuessResult evaluation, formatting, and validation."""

    def setUp(self) -> None:
        self.secret = "crane"
        self.bad_words = ["plant", "bongo", "brick", "flint", "gloom"]

    def _reversed_secret(self) -> str:
        """Return the reversed secret word ('enarc' for 'crane')."""
        return self.secret[::-1]

    def test_exact_match_sets_matched_state_and_all_correct(self) -> None:
        """Verify an exact guess marks every letter CORRECT and sets State.MATCHED."""
        result = GuessResult(self.secret, self.secret)

        self.assertEqual(result.guess, "crane")
        self.assertIs(result.state, State.MATCHED)
        self.assertEqual(result.outcomes, [Outcome.CORRECT] * len(self.secret))
        self.assertEqual(str(result), "🟩🟩🟩🟩🟩")

    def test_reversed_word_evaluates_positions_and_duplicate_counts(self) -> None:
        """Verify reversed guess ('enarc' vs 'crane') handles exact, misplaced, and extra letters."""
        # 'crane' vs 'enarc':
        # pos 0: e (not in crane) -> ABSENT
        # pos 1: n (in crane at idx 3) -> PRESENT
        # pos 2: a (exact match at idx 2 in crane) -> CORRECT
        # pos 3: r (in crane at idx 1) -> PRESENT
        # pos 4: c (in crane at idx 0) -> PRESENT
        result = GuessResult(self._reversed_secret(), self.secret)

        self.assertEqual(result.guess, "enarc")
        self.assertIs(result.state, State.UNMATCHED)
        self.assertEqual(
            result.outcomes,
            [
                Outcome.PRESENT,
                Outcome.PRESENT,
                Outcome.CORRECT,
                Outcome.PRESENT,
                Outcome.PRESENT,
            ],
        )
        self.assertEqual(str(result), "🟨🟨🟩🟨🟨")

    def test_duplicate_letters_do_not_over_award_present(self) -> None:
        """Verify repeated guess letters are only marked PRESENT up to remaining secret count."""
        # Secret "crane" has only one 'a'; guess "aaabb" has three 'a's:
        # pos 0: a -> PRESENT (uses the single 'a' in 'crane')
        # pos 1: a -> ABSENT (no 'a' left)
        # pos 2: a -> ABSENT (no 'a' left)
        # pos 3: b -> ABSENT
        # pos 4: b -> ABSENT
        result = GuessResult(guess="aaabb", secret=self.secret)
        self.assertIs(result.state, State.UNMATCHED)
        self.assertEqual(
            result.outcomes,
            [
                Outcome.ABSENT,
                Outcome.ABSENT,
                Outcome.CORRECT,
                Outcome.ABSENT,
                Outcome.ABSENT,
            ],
        )
        print(result.outcomes)

    def test_bad_word_batch_stays_unmatched(self) -> None:
        """Verify non-matching candidate words stay UNMATCHED and never all-CORRECT."""
        for word in self.bad_words:
            with self.subTest(word=word):
                result = GuessResult(word, self.secret)
                self.assertIs(result.state, State.UNMATCHED)
                self.assertEqual(len(result.outcomes), len(self.secret))
                self.assertNotEqual(
                    result.outcomes,
                    [Outcome.CORRECT] * len(self.secret),
                )

    def test_from_guess_normalizes_whitespace_and_case(self) -> None:
        """Verify from_guess() strips and lowercases guess and secret inputs."""
        result = GuessResult.from_guess("  CRANE  ", "  Crane ")

        self.assertEqual(result.guess, "crane")
        self.assertIs(result.state, State.MATCHED)
        self.assertEqual(result.outcomes, [Outcome.CORRECT] * 5)

    def test_mismatched_or_empty_inputs_raise_value_error(self) -> None:
        """Verify mismatched lengths or blank strings raise ValueError."""
        with self.assertRaises(ValueError):
            GuessResult("cra", self.secret)

        with self.assertRaises(ValueError):
            GuessResult("cranes", self.secret)

        with self.assertRaises(ValueError):
            GuessResult("   ", self.secret)

        with self.assertRaises(ValueError):
            GuessResult(self.secret, "")

    def test_non_string_inputs_raise_type_error(self) -> None:
        """Verify non-string guess or secret raises TypeError."""
        with self.assertRaises(TypeError):
            GuessResult(12345, self.secret)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            GuessResult(self.secret, None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()