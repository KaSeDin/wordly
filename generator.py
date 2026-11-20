from wonderwords import RandomWord
from dataclasses import dataclass,field
from validators import validate_positive_int

@dataclass
class Generator:
    size:int
    word_count:int
    rw:RandomWord=field(default_factory=RandomWord,repr=False)

    def __post_init__(self) -> None:
        validate_positive_int("size", self.size)
        validate_positive_int("word_count", self.word_count)
        if not hasattr(self.rw, "word"):
            raise TypeError("rw must be a RandomWord instance with a .word() method")
        
    def __str__(self)->str:
            return f"Generator(size={self.size}, word_count={self.word_count})"

    @classmethod
    def from_config(cls, cfg) -> "Generator":
        return cls(
            size=cfg.word_length,
            word_count=cfg.word_count,
        )
    
    def getWord(self)->str:
        try :
            word = self.rw.word(
                word_min_length=self.size,
                word_max_length=self.size,
                exclude_with_spaces=True
            )
        except Exception as err:
            raise RuntimeError(
                f"Failed to generate word of length {self.size}: {err}"
            ) from err
        if not word or not isinstance(word, str):
            raise RuntimeError(f"Unexpected word returned from RandomWord: {word!r}")
        return word.strip().lower()
    
    def getWords(self)->list[str]:
        words:list[str]=[]
        for i in range(self.word_count):
            words.append(self.getWord())
        return words