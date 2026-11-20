from dataclasses import replace
from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module
from history import History
from temp.game import Game
from temp.guessresult import GuessResult
from temp.state import Result, State


class TestHistoryWithRealConfig(unittest.TestCase):
    """Unit/integration tests for History using the real Config and a temporary history file."""

    def setUp(self) -> None:
        """Create an isolated temporary history file while keeping real Config values."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        temp_history_path = Path(self.tmp_dir.name) / "test_history.json"

        self.cfg = replace(config_module.config, history_file=temp_history_path)
        self.history_file = self.cfg.history_file
        self.history = History.from_config(self.cfg)

    def tearDown(self) -> None:
        """Clean up temporary files and directories after each test."""
        self.tmp_dir.cleanup()

    def test_initial_history_file_created_empty(self) -> None:
        """Verify History initializes an empty JSON object file on creation."""
        self.assertTrue(self.history_file.exists())
        self.assertEqual(self.history.load_stats(), {})
        self.assertEqual(self.history.history_path, self.history_file)

    def test_save_and_load_stats(self) -> None:
        """Verify save_stats() persists a dictionary and load_stats() reads it back."""
        payload = {
            "key": {
                "secret": "secret",
                "guess_count": 0,
                "result": Result.UNFINISHED.name,
                "guess": [],
            }
        }
        self.history.save_stats(payload)
        self.assertEqual(self.history.load_stats(), payload)

    def test_update_stats_creates_entry_with_started_at_timestamp(self) -> None:
        """Verify update_stats() creates a new game entry with a timezone-aware started_at."""
        game = Game(secret="secret", cfg=self.cfg, history=self.history)
        self.history.update_stats("game_1", game)

        data = self.history.load_stats()
        self.assertIn("game_1", data)
        entry = data["game_1"]
        self.assertEqual(entry["secret"], "secret")
        self.assertEqual(entry["guess_count"], 0)
        self.assertEqual(entry["result"], Result.UNFINISHED.name)
        self.assertEqual(entry["guess"], [])
        self.assertIn("started_at", entry)

        parsed_ts = datetime.fromisoformat(entry["started_at"])
        self.assertIsNotNone(parsed_ts.tzinfo)

    def test_update_stats_appends_guesses_and_preserves_started_at(self) -> None:
        """Verify guesses append in order, update game state, and keep initial started_at."""
        game = Game(secret="apple", cfg=self.cfg, history=self.history)
        self.history.update_stats("game_1", game)
        initial_started_at = self.history.load_stats()["game_1"]["started_at"]

        guess_1 = GuessResult(guess="crane", secret="apple")
        game.guess_count = 1
        self.history.update_stats("game_1", game, new_guess=guess_1)

        guess_2 = GuessResult(guess="apple", secret="apple")
        game.guess_count = 2
        game.result = Result.WIN
        self.history.update_stats("game_1", game, new_guess=guess_2)

        data = self.history.load_stats()
        entry = data["game_1"]

        self.assertEqual(entry["started_at"], initial_started_at)
        self.assertEqual(entry["guess_count"], 2)
        self.assertEqual(entry["result"], Result.WIN.name)
        self.assertEqual(len(entry["guess"]), 2)

        self.assertEqual(entry["guess"][0]["guess"], "crane")
        self.assertEqual(entry["guess"][0]["state"], State.UNMATCHED.name)
        self.assertEqual(entry["guess"][0]["outcomes"], "⬛⬛🟨⬛🟩")
        self.assertIsNotNone(datetime.fromisoformat(entry["guess"][0]["guessed_at"]))

        self.assertEqual(entry["guess"][1]["guess"], "apple")
        self.assertEqual(entry["guess"][1]["state"], State.MATCHED.name)
        self.assertEqual(entry["guess"][1]["outcomes"], "🟩🟩🟩🟩🟩")
        self.assertIsNotNone(datetime.fromisoformat(entry["guess"][1]["guessed_at"]))

    def test_multiple_keys_do_not_overwrite_each_other(self) -> None:
        """Verify separate game keys coexist independently in the history file."""
        game_1 = Game(secret="apple", cfg=self.cfg, history=self.history)
        game_2 = Game(secret="grape", cfg=self.cfg, history=self.history)

        self.history.update_stats("game_1", game_1)
        self.history.update_stats("game_2", game_2)

        data = self.history.load_stats()
        self.assertEqual(set(data.keys()), {"game_1", "game_2"})
        self.assertEqual(data["game_1"]["secret"], "apple")
        self.assertEqual(data["game_2"]["secret"], "grape")

    def test_print_history_formats_recorded_game(self) -> None:
        """Verify print_history() returns a formatted report containing game and guess details."""
        game = Game(secret="apple", cfg=self.cfg, history=self.history)
        self.history.update_stats("game_1", game)

        guess_1 = GuessResult(guess="apple", secret="apple")
        game.guess_count = 1
        game.result = Result.WIN
        self.history.update_stats("game_1", game, new_guess=guess_1)

        report = self.history.print_history()
        self.assertIn("Game: game_1", report)
        self.assertIn("Secret: apple", report)
        self.assertIn("Result: WIN (Guesses: 1)", report)
        self.assertIn("apple | 🟩🟩🟩🟩🟩 | MATCHED", report)

    def test_load_stats_returns_empty_dict_if_file_deleted(self) -> None:
        """Verify load_stats() gracefully returns {} if the history file is missing."""
        self.history_file.unlink()
        self.assertEqual(self.history.load_stats(), {})

    def test_load_stats_raises_runtime_error_on_corrupted_json(self) -> None:
        """Verify load_stats() wraps invalid JSON in RuntimeError."""
        self.history_file.write_text("{invalid json", encoding="utf-8")
        with self.assertRaises(RuntimeError) as ctx:
            self.history.load_stats()

        self.assertIn("Failed to load history", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()