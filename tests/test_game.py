from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module
from game import Game
from state import Result, State
from history import History

class TestGame(unittest.TestCase):
    def setUp(self):

        self.test_file = Path(__file__).resolve().parent / "test_game_secrets.txt"
        self.history_file=Path(__file__).resolve().parent / "history.json"
        self.test_file.write_text("", encoding="utf-8")
        self.cfg = config_module.Config(
            secrets_file=self.test_file,
            word_length=5,
            word_count=3,
            max_guesses=6,
            history_file=self.history_file
        )
        self.history=History(self.cfg)
        self.secret = "crane"
        self.game = Game(self.secret, self.cfg,self.history)

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_init_sets_initial_state(self):
        self.assertEqual(self.game.secret, self.secret)
        self.assertIs(self.game.cfg, self.cfg)
        self.assertEqual(self.game.guess_count, 0)
        self.assertIs(self.game.result, Result.UNFINISHED)
        self.assertEqual(self.game.guesses, [])

    def test_single_incorrect_guess_stays_unfinished(self):
        self.game.make_guess("plant")
        self.assertEqual(self.game.guess_count, 1)
        self.assertEqual(len(self.game.guesses), 1)
        self.assertIs(self.game.guesses[0].state, State.UNMATCHED)
        self.assertIs(self.game.result, Result.UNFINISHED)

    def test_winning_guess_sets_win_result(self):
        self.game.make_guess("plant")
        self.game.make_guess("crane")
        self.assertEqual(self.game.guess_count, 2)
        self.assertEqual(len(self.game.guesses), 2)
        self.assertIs(self.game.guesses[-1].state, State.MATCHED)
        self.assertIs(self.game.result, Result.WIN)

    def test_winning_on_final_guess_sets_win_not_loss(self):
        cfg = config_module.Config(
            secrets_file=self.test_file,
            word_length=5,
            word_count=3,
            max_guesses=2,
            history_file=self.history_file
        )
        game = Game(self.secret, cfg,self.history)
        game.make_guess("plant")
        game.make_guess("crane")
        self.assertEqual(game.guess_count, 2)
        self.assertIs(game.result, Result.WIN)

    def test_reaching_max_guesses_without_match_sets_loss(self):
        cfg = config_module.Config(
            secrets_file=self.test_file,
            word_length=5,
            word_count=3,
            max_guesses=3,
            history_file=self.history_file
        )
        game = Game(self.secret, cfg,self.history)
        for word in ["plant", "bongo", "brick"]:
            game.make_guess(word)
        self.assertEqual(game.guess_count, 3)
        self.assertEqual(len(game.guesses), 3)
        self.assertIs(game.result, Result.LOSS)

    def test_guess_after_win_raises_exception(self):
        self.game.make_guess("crane")
        self.assertIs(self.game.result, Result.WIN)
        with self.assertRaises(Exception):
            self.game.make_guess("plant")

    def test_guess_after_loss_raises_exception(self):
        cfg = config_module.Config(
            secrets_file=self.test_file,
            word_length=5,
            word_count=3,
            max_guesses=1,
            history_file=self.history_file
        )
        game = Game(self.secret, cfg,self.history)
        game.make_guess("plant")
        self.assertIs(game.result, Result.LOSS)
        with self.assertRaises(Exception):
            game.make_guess("crane")


if __name__ == "__main__":
    unittest.main()