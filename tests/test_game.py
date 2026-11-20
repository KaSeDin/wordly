from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module
from game import Game
from history import History
from state import Result, State


class TestGame(unittest.TestCase):
    """Tests for Game using the real config_module.config with isolated temp files."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        tmp_path = Path(self.tmp_dir.name)
        secrets_file = tmp_path / "test_game_secrets.txt"
        history_file = tmp_path / "history.json"
        secrets_file.write_text("", encoding="utf-8")

        # Start from the real config object; only redirect file paths to temp files
        self.cfg = replace(
            config_module.config,
            secrets_file=secrets_file,
            history_file=history_file,
        )
        self.history = History.from_config(self.cfg)
        self.secret = "a" * self.cfg.word_length
        self.wrong_guess = "b" * self.cfg.word_length
        self.game = Game(
            secret=self.secret,
            cfg=self.cfg,
            history=self.history,
            auto_start=False,
        )

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_init_sets_initial_state(self) -> None:
        self.assertEqual(self.game.secret, self.secret)
        self.assertIs(self.game.cfg, self.cfg)
        self.assertEqual(self.game.guess_count, 0)
        self.assertIs(self.game.result, Result.UNFINISHED)
        self.assertEqual(self.game.guesses, [])

    def test_single_incorrect_guess_stays_unfinished(self) -> None:
        Game._make_guess(self.game, self.wrong_guess)
        self.assertEqual(self.game.guess_count, 1)
        self.assertEqual(len(self.game.guesses), 1)
        self.assertIs(self.game.guesses[0].state, State.UNMATCHED)
        self.assertIs(self.game.result, Result.UNFINISHED)

    def test_length_mismatch_does_not_consume_guess(self) -> None:
        with self.assertRaises(ValueError):
            Game._make_guess(self.game, self.secret[:-1])

        self.assertEqual(self.game.guess_count, 0)
        self.assertEqual(self.game.guesses, [])
        history_entry = self.history.load_stats()[self.game.game_id]
        self.assertEqual(history_entry["guess_count"], 0)
        self.assertEqual(history_entry["guess"], [])

    def test_winning_guess_sets_win_result(self) -> None:
        Game._make_guess(self.game, self.wrong_guess)
        Game._make_guess(self.game, self.secret)
        self.assertEqual(self.game.guess_count, 2)
        self.assertEqual(len(self.game.guesses), 2)
        self.assertIs(self.game.guesses[-1].state, State.MATCHED)
        self.assertIs(self.game.result, Result.WIN)

    def test_winning_on_final_guess_sets_win_not_loss(self) -> None:
        for _ in range(self.cfg.max_guesses - 1):
            Game._make_guess(self.game, self.wrong_guess)
        Game._make_guess(self.game, self.secret)
        self.assertEqual(self.game.guess_count, self.cfg.max_guesses)
        self.assertIs(self.game.result, Result.WIN)

    def test_reaching_max_guesses_without_match_sets_loss(self) -> None:
        for _ in range(self.cfg.max_guesses):
            Game._make_guess(self.game, self.wrong_guess)
        self.assertEqual(self.game.guess_count, self.cfg.max_guesses)
        self.assertEqual(len(self.game.guesses), self.cfg.max_guesses)
        self.assertIs(self.game.result, Result.LOSS)

    def test_guess_after_win_raises_runtime_error(self) -> None:
        Game._make_guess(self.game, self.secret)
        self.assertIs(self.game.result, Result.WIN)
        with self.assertRaises(RuntimeError):
            Game._make_guess(self.game, self.wrong_guess)

    def test_guess_after_loss_raises_runtime_error(self) -> None:
        for _ in range(self.cfg.max_guesses):
            Game._make_guess(self.game, self.wrong_guess)
        self.assertIs(self.game.result, Result.LOSS)
        with self.assertRaises(RuntimeError):
            Game._make_guess(self.game, self.secret)

    def test_auto_start_runs_input_loop_and_stops_on_win(self) -> None:
        inputs = [self.secret + "x", self.wrong_guess, self.secret, self.wrong_guess]
        output = StringIO()
        with patch("builtins.input", side_effect=inputs), redirect_stdout(output):
            game = Game(
                secret=self.secret,
                cfg=self.cfg,
                history=self.history,
                auto_start=True,
            )
        self.assertEqual(game.guess_count, 2)
        self.assertIs(game.result, Result.WIN)
        self.assertIn("WORDLE CHALLENGE", output.getvalue())
        self.assertIn("Attempt 1/", output.getvalue())
        self.assertEqual(output.getvalue().count("Attempt 1/"), 2)
        self.assertIn("Guess must be exactly", output.getvalue())
        self.assertIn("Brilliant! You solved it in 2 guesses!", output.getvalue())

    def test_games_with_same_secret_keep_separate_history(self) -> None:
        Game._make_guess(self.game, self.wrong_guess)
        second_game = Game(
            secret=self.secret,
            cfg=self.cfg,
            history=self.history,
            auto_start=False,
        )
        Game._make_guess(second_game, self.secret)

        history = self.history.load_stats()
        self.assertEqual(len(history), 2)
        self.assertNotEqual(self.game.game_id, second_game.game_id)
        self.assertEqual(history[self.game.game_id]["guess_count"], 1)
        self.assertEqual(history[second_game.game_id]["guess_count"], 1)
        self.assertEqual(history[self.game.game_id]["result"], Result.UNFINISHED.name)
        self.assertEqual(history[second_game.game_id]["result"], Result.WIN.name)
        self.assertEqual(len(history[self.game.game_id]["guess"]), 1)
        self.assertEqual(len(history[second_game.game_id]["guess"]), 1)
        self.assertEqual(
            history[second_game.game_id]["guess"][0]["state"], State.MATCHED.name
        )


if __name__ == "__main__":
    unittest.main()