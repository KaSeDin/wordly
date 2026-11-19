from enum import Enum

class State(Enum):
    MATCHED="matched"
    UNMATCHED="unmatched"
    NOT_STARTED="not_started"

class Result(Enum):
    WIN="win"
    LOSS="loss"
    ABORT="abort"
    UNFINISHED="unfinished"