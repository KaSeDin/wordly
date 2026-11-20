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
from game import Game
from guessresult import GuessResult
from history import History
from state import Result, State


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
        if hasattr(self, "history_file") and self.history_file is not None:
            self.history_file.unlink(missing_ok=True)
        if hasattr(self, "tmp_dir") and self.tmp_dir is not None:
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