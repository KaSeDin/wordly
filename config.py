import os
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

    
@dataclass(frozen=True)
class Config:
    secrets_file:Path
    word_length:int
    word_count:int
    max_guesses:int
    history_file:Path

    def __post_init__(self) -> None:
        self._validate_positive_int("word_length", self.word_length)
        self._validate_positive_int("word_count", self.word_count)
        self._validate_positive_int("max_guesses", self.max_guesses)
        self._validate_path("secrets_file", self.secrets_file)
        self._validate_path("history_file", self.history_file)
        
    @staticmethod
    def _validate_positive_int(field_name: str, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"Config '{field_name}' must be a positive integer, got {value!r}")

    @staticmethod
    def _validate_path(field_name: str, value: Path) -> None:
        if not isinstance(value, Path) or not str(value).strip():
            raise ValueError(f"Config '{field_name}' must be a valid non-empty Path, got {value!r}")
        
    @staticmethod
    def _env_int(name: str) -> int:
        raw = os.getenv(name)
        if raw is None or not raw.strip():
            raise ValueError(f"Environment variable '{name}' is not set")
        try:
            return int(raw.strip())
        except ValueError as err:
            raise ValueError(f"Environment variable '{name}' must be an integer, got {raw!r}") from err

    @staticmethod
    def _env_path(name: str) -> Path:
        raw = os.getenv(name)
        if raw is None or not raw.strip():
            raise ValueError(f"Environment variable '{name}' is not set")
        return Path(raw.strip())

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            secrets_file=cls._env_path("SECRETS_FILE"),
            word_length=cls._env_int("WORD_LENGTH"),
            word_count=cls._env_int("WORD_COUNT"),
            max_guesses=cls._env_int("MAX_GUESSES"),
            history_file=cls._env_path("HISTORY_FILE"),
        )

    def __str__(self) -> str:
        return (
            "Configuration:\n"
            f"  Secrets File : {self.secrets_file}\n"
            f"  History File : {self.history_file}\n"
            f"  Word Length  : {self.word_length}\n"
            f"  Word Count   : {self.word_count}\n"
            f"  Max Guesses  : {self.max_guesses}"
        )

def load_config() -> Config:
    try:
        return Config.from_env()
    except (ValueError) as err:
        raise RuntimeError(f"Failed to load configuration: {err}") from err

config=load_config()
