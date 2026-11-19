import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_int(name:str) -> int:
    value=os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return int(value)

def _get_path(name:str)->Path:
    value=os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set")
    return Path(value)
    
@dataclass(frozen=True)
class Config:
    secrets_file:Path
    word_length:int
    word_count:int

def load_config() -> Config:
    return Config(
        secrets_file=_get_path("SECRETS_FILE"),
        word_length=_get_int("WORD_LENGTH"),
        word_count=_get_int("WORD_COUNT")
    )

config=load_config()
