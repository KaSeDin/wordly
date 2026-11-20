from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from wordle import Wordle
from state import Result


class TestWordle(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = SimpleNamespace(word_length=5, max_guesses=6)
        with (
            patch("wordle.config.config", self.cfg),
            patch("wordle.History"),
            patch("wordle.Secrets"),
        ):
            self.wordle = Wordle()

    def test_commands_are_registered_and_listed_in_help(self) -> None:
        expected_commands = {"stats", "reset_stats", "rules", "clear"}
        self.assertTrue(expected_commands.issubset(self.wordle.commands))
        self.assertTrue(expected_commands.issubset(self.wordle.descriptions))

        output = StringIO()
        with redirect_stdout(output):
            self.wordle.cmd_help()

        for command in expected_commands:
            self.assertIn(command, output.getvalue())

    def test_rules_include_configured_game_settings(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(self.wordle.execute("rules"))

        self.assertIn("exactly 5 letters", output.getvalue())
        self.assertIn("6 guesses", output.getvalue())

    def test_clear_emits_terminal_clear_sequence(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            self.assertTrue(self.wordle.execute("clear"))

        self.assertEqual(output.getvalue(), "\033[2J\033[H")

    def test_view_history_prints_report(self) -> None:
        self.wordle.history.print_history.return_value = "Game: game-id"
        output = StringIO()

        with redirect_stdout(output):
            self.assertTrue(self.wordle.execute("view_history"))

        self.assertIn("Game: game-id", output.getvalue())

    def test_stats_count_all_saved_games(self) -> None:
        self.wordle.history.load_stats.return_value = {
            "win": {"result": Result.WIN.name, "guess_count": 4},
            "loss": {"result": Result.LOSS.name, "guess_count": 6},
            "unfinished": {"result": Result.UNFINISHED.name, "guess_count": 2},
            "aborted": {"result": Result.ABORT.name, "guess_count": 1},
        }
        output = StringIO()

        with redirect_stdout(output):
            self.assertTrue(self.wordle.execute("stats"))

        self.assertIn("Games played: 4", output.getvalue())
        self.assertIn("Wins: 1", output.getvalue())
        self.assertIn("Losses: 1", output.getvalue())
        self.assertIn("Win rate: 25.0%", output.getvalue())
        self.assertIn("Average guesses: 3.25", output.getvalue())

    def test_stats_report_current_and_best_win_streaks(self) -> None:
        self.wordle.history.load_stats.return_value = {
            "win-1": {"result": Result.WIN.name, "guess_count": 1},
            "win-2": {"result": Result.WIN.name, "guess_count": 2},
            "win-3": {"result": Result.WIN.name, "guess_count": 3},
            "loss": {"result": Result.LOSS.name, "guess_count": 6},
            "win-4": {"result": Result.WIN.name, "guess_count": 1},
            "win-5": {"result": Result.WIN.name, "guess_count": 2},
        }
        output = StringIO()

        with redirect_stdout(output):
            self.wordle.cmd_stats()

        self.assertIn("Current streak: 2", output.getvalue())
        self.assertIn("Best streak: 3", output.getvalue())

    def test_reset_stats_clears_history_after_confirmation(self) -> None:
        with patch("builtins.input", return_value="yes"):
            self.assertTrue(self.wordle.execute("reset_stats"))

        self.wordle.history.save_stats.assert_called_once_with({})

    def test_reset_stats_preserves_history_without_confirmation(self) -> None:
        output = StringIO()
        with patch("builtins.input", return_value="no"), redirect_stdout(output):
            self.assertTrue(self.wordle.execute("reset_stats"))

        self.wordle.history.save_stats.assert_not_called()
        self.assertIn("Reset cancelled.", output.getvalue())

    def test_start_game_uses_secret_and_starts_game(self) -> None:
        self.wordle.secrets.get_secret.return_value = "crane"
        with patch("wordle.Game") as game_class:
            self.assertTrue(self.wordle.execute("new_game"))

        game_class.assert_called_once_with(
            "crane", self.cfg, self.wordle.history, True
        )


if __name__ == "__main__":
    unittest.main()
