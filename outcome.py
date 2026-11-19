from enum import Enum 

class Outcome(Enum):
    CORRECT="correct"
    PRESENT="present"
    ABSENT="absent"

class Symbol(Enum):
    CORRECT="🟩"
    PRESENT="🟨"
    ABSENT="⬛"