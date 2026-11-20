from wonderwords import RandomWord
from dataclasses import dataclass,field
from validators import validate_positive_int,validate_not_none,validate_has_attr,validate_isinstance
from typing import Any

@dataclass
class Generator:
    cfg:Any
    rw:RandomWord=field(default_factory=RandomWord,repr=False)

    def __post_init__(self) -> None:
        validate_not_none("cfg",self.cfg)
        validate_positive_int("size", self.cfg.word_length)
        validate_positive_int("word_count", self.cfg.word_count)
        validate_has_attr("rw",self.rw,"word",callable_required=True)
        
    def __str__(self)->str:
        return f"Generator(size={self.cfg.word_length}, word_count={self.cfg.word_count})"

    @classmethod
    def from_config(cls, cfg) -> "Generator":
        return cls(
            cfg=cfg
        )
    
    def getWord(self)->str:
        try :
            word = self.rw.word(
                word_min_length=self.cfg.word_length,
                word_max_length=self.cfg.word_length,
                exclude_with_spaces=True
            )
        except Exception as err:
            raise RuntimeError(
                f"Failed to generate word of length {self.cfg.word_length}: {err}"
            ) from err
        validate_isinstance("word",word,str)
        return word.strip().lower()
    
    def getWords(self)->list[str]:
        words:list[str]=[]
        for i in range(self.cfg.word_count):
            words.append(self.getWord())
        return words