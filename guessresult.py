from dataclasses import InitVar, dataclass, field
from validators import validate_isinstance
from temp.state import State 
from temp.outcome import Outcome,Symbol

@dataclass
class GuessResult:
    guess:str
    secret:str
    state:State=field(default=State.NOT_STARTED)
    outcomes:list[Outcome]=field(default_factory=list,init=False)

    def __post_init__(self) -> None:
        validate_isinstance("guess",self.guess,str)
        validate_isinstance("secret",self.secret,str)
        validate_isinstance("state",self.state,State)
        
        self.guess=self.guess.strip().lower()
        self.secret=self.strip().lower()

        if not self.guess or not self.secret:
            raise ValueError("guess and secret must be non-empty strings")
        if len(self.guess) != len(self.secret):
            raise ValueError(
                f"guess length ({len(self.guess)}) must match "
                f"secret length ({len(self.secret)})"
            )
        self.outcomes, self.state = self._eval_guess(self.guess, self.secret)

    def __str__(self) -> str:
        return "".join(outcome.symbol for outcome in self.outcomes)

    @staticmethod
    def _eval_guess(guess: str, secret: str) -> tuple[list[Outcome], State]:
        try:
            word_len = len(secret)
            remaining_counts: dict[str, int] = {}
            outcomes: list[Outcome] = []
            all_matched = True

            # Pass 1: mark exact positional matches and count unmatched secret letters
            for i in range(word_len):
                if secret[i] == guess[i]:
                    outcomes.append(Outcome.CORRECT)
                else:
                    all_matched = False
                    outcomes.append(Outcome.ABSENT)
                    secret_char = secret[i]
                    remaining_counts[secret_char] = remaining_counts.get(secret_char, 0) + 1

            if all_matched:
                return outcomes, State.MATCHED

            # Pass 2: mark misplaced letters (PRESENT) without exceeding remaining counts
            for i in range(word_len):
                if outcomes[i] == Outcome.CORRECT:
                    continue
                guess_char = guess[i]
                if remaining_counts.get(guess_char, 0) > 0:
                    outcomes[i] = Outcome.PRESENT
                    remaining_counts[guess_char] -= 1

            return outcomes, State.UNMATCHED
        except Exception as err:
            raise RuntimeError(
                f"Failed to evaluate guess {guess!r} against secret: {err}"
            ) from err