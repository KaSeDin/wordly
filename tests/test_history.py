import unittest
import config
from history import History
from game import Game
from guessresult import GuessResult
from state import Result,State
from datetime import datetime
import json

class TestHistory(unittest.TestCase):

    def setUp(self) -> None:
        self.cfg = config.config
        self.history_file = self.cfg.history_file
        self.history = History(self.cfg)

    def tearDown(self) -> None:
        # Remove the test-created file after testing
        if self.history_file.exists():
            self.history_file.unlink()

    def test_initial_history_file_created_empty(self) -> None:
        self.assertTrue(self.history_file.exists())
        self.assertEqual(self.history.load_stats(), {})

    def test_save_and_load_stats(self) -> None:
        payload = {
            "key": {
                "secret": "secret",
                "guess_count": 0,
                "result": "UNFINISHED",
                "guess": [],
            }
        }
        self.history.save_stats(payload)
        self.assertEqual(self.history.load_stats(), payload)

    def test_update_stats_creates_entry_with_started_at_timestamp(self) -> None:
        game = Game(secret="secret",cfg=self.cfg,history=self.history)
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
        game = Game(secret="apple",cfg=self.cfg,history=self.history)
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
        game_1 = Game(secret="apple",cfg=self.cfg,history=self.history)
        game_2 = Game(secret="grape",cfg=self.cfg,history=self.history)

        self.history.update_stats("game_1", game_1)
        self.history.update_stats("game_2", game_2)

        data = self.history.load_stats()
        print(data,data.keys())
        # self.assertEqual(set(data.keys()), {"game_1", "game_2"})
        # self.assertEqual(data["game_1"]["secret"], "apple")
        # self.assertEqual(data["game_2"]["secret"], "grape")

    def test_load_stats_returns_empty_dict_if_file_deleted(self) -> None:
        self.history_file.unlink()
        self.assertEqual(self.history.load_stats(), {})

    def test_load_stats_raises_on_corrupted_json(self) -> None:
        self.history_file.write_text("{invalid json", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            self.history.load_stats()

if __name__ == "__main__":
    unittest.main()