from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4
from validators import *
from state import State,Result
from guessresult import GuessResult

@dataclass
class Game:
    secret:str
    cfg:Any
    history:Any
    auto_start: bool = field(default=False, repr=False)
    game_id: str = field(default_factory=lambda: uuid4().hex, init=False, repr=False)
    guess_count:int = field(default=0,init=False)
    result: Result = field(default=Result.UNFINISHED, init=False)
    guesses: list[GuessResult] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        validate_not_none("cfg",self.cfg)
        validate_not_none("history",self.history)
        validate_isinstance("secret",self.secret,str)
        validate_positive_int("cfg.max_guesses",self.cfg.max_guesses)

        self.secret = self.secret.strip().lower()
        if not self.secret:
            raise ValueError("secret must be a non-empty string")
        self.secret = self.secret

        try:
            self.history.update_stats(self.game_id, self)
        except RuntimeError:
            raise
        except Exception as err:
            raise RuntimeError(f"Failed to record initial game state: {err}") from err

        if self.auto_start:
            self._start_game(self)

    def __str__(self) -> str:
        return (
            f"Game(secret={self.secret!r}, guess_count={self.guess_count}/"
            f"{self.cfg.max_guesses}, result={self.result.name})"
        )

    @staticmethod
    def _make_guess(game: "Game", guess: str) -> GuessResult:
        validate_not_none("game", game)
        validate_isinstance("guess", guess, str)

        if game.result.is_terminal:
            raise RuntimeError("Game is already finished; create a new Game")

        cleaned_guess = guess.strip().lower()
        if not cleaned_guess:
            raise ValueError("Guess must be a non-empty string")

        try:
            guess_result = GuessResult(cleaned_guess, game.secret)
            game.guess_count += 1
            game.guesses.append(guess_result)

            if guess_result.state == State.MATCHED:
                game.result = Result.WIN
            elif game.guess_count >= game.cfg.max_guesses:
                game.result = Result.LOSS

            game.history.update_stats(game.game_id, game, guess_result)
            return guess_result
        except (ValueError, RuntimeError):
            raise
        except Exception as err:
            raise RuntimeError(f"Failed while processing guess {guess!r}: {err}") from err
        
    @staticmethod
    def _start_game(game: "Game") -> None:
        validate_not_none("game", game)
        print("\n" + "=" * 40)
        print("WORDLE CHALLENGE")
        print(f"Guess the {len(game.secret)}-letter word in {game.cfg.max_guesses} tries.")
        print("🟩 Correct  🟨 In the word, wrong spot  ⬛ Not in the word")
        print(f"Status: {game.result.label}")
        print("=" * 40)
        try:
            while (
                game.guess_count < game.cfg.max_guesses
                and not game.result.is_terminal
            ):
                print(f"\nAttempt {game.guess_count + 1}/{game.cfg.max_guesses}")
                new_guess = input("Your guess: ").strip()
                if len(new_guess) != len(game.secret):
                    print(
                        f"Guess must be exactly {len(game.secret)} letters long. "
                        "Please try again."
                    )
                    continue

                guess_result = Game._make_guess(game, new_guess)
                print(f"{guess_result}  {guess_result.state.label}")
                if game.result is Result.WIN:
                    print(f"Brilliant! You solved it in {game.guess_count} "
                          f"{'guess' if game.guess_count == 1 else 'guesses'}!")
                elif game.result is Result.LOSS:
                    print(f"Out of guesses! The word was {game.secret.upper()}.")
                else:
                    remaining = game.cfg.max_guesses - game.guess_count
                    print(f"{remaining} {'guess' if remaining == 1 else 'guesses'} remaining.")
        except (ValueError, RuntimeError):
            raise
        except Exception as err:
            raise RuntimeError(f"Game loop terminated unexpectedly: {err}") from err

    @classmethod
    def from_config(
        cls,
        cfg: Any,
        secret: str | None = None,
        history: Any | None = None,
        auto_start: bool = True,
    ) -> "Game":
        validate_not_none("cfg", cfg)
        try:
            resolved_secret = secret if secret is not None else Secrets(cfg).get_secret()
            resolved_history = history if history is not None else History.from_config(cfg)
            return cls(
                secret=resolved_secret,
                cfg=cfg,
                history=resolved_history,
                auto_start=auto_start,
            )
        except (ValueError, RuntimeError):
            raise
        except Exception as err:
            raise RuntimeError(f"Failed to initialize Game from config: {err}") from err