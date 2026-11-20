from enum import Enum


class Outcome(Enum):
    CORRECT = "correct"
    PRESENT = "present"
    ABSENT = "absent"

    @property
    def symbol(self) -> str:
        symbols = {
            Outcome.CORRECT: "🟩",
            Outcome.PRESENT: "🟨",
            Outcome.ABSENT: "⬛",
        }
        return symbols[self]