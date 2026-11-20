from enum import Enum


class State(Enum):
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    NOT_STARTED = "not_started"

    @property
    def is_evaluated(self) -> bool:
        """Whether a guess has been evaluated against the secret."""
        return self in (State.MATCHED, State.UNMATCHED)

    @property
    def label(self) -> str:
        labels = {
            State.MATCHED: "Matched",
            State.UNMATCHED: "Unmatched",
            State.NOT_STARTED: "Not Started",
        }
        return labels[self]


class Result(Enum):
    WIN = "win"
    LOSS = "loss"
    ABORT = "abort"
    UNFINISHED = "unfinished"

    @property
    def is_terminal(self) -> bool:
        """Whether the game has ended and no more guesses should be accepted."""
        return self in (Result.WIN, Result.LOSS, Result.ABORT)

    @property
    def label(self) -> str:
        labels = {
            Result.WIN: "Victory",
            Result.LOSS: "Out of Guesses",
            Result.ABORT: "Aborted",
            Result.UNFINISHED: "In Progress",
        }
        return labels[self]