from dataclasses import dataclass, field
from pathlib import Path
import random
from generator import Generator
from validators import validate_non_empty_path,validate_not_none,validate_has_attr
from typing import Any

@dataclass
class Secrets:
    cfg:Any
    random:random.Random=field(default_factory=random.Random,repr=False)
    generator: Generator | None = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        validate_not_none("cfg",self.cfg)
        validate_non_empty_path("cfg.secrets_file", self.cfg.secrets_file)

        if self.generator is None:
            self.generator = Generator(self.cfg)

        validate_not_none("generator", self.generator)
        validate_has_attr("random", self.random, "choice", callable_required=True)
        validate_has_attr("generator", self.generator, "getWord", callable_required=True)
        validate_has_attr("generator", self.generator, "getWords", callable_required=True)

    @property
    def words_path(self) -> Path:
        return self.cfg.secrets_file
    
    def __str__(self) -> str:
        return f"Secrets(words_path={self.words_path})"

    @classmethod
    def from_config(cls, cfg) -> "Secrets":
        return cls(
            cfg=cfg
        )

    @staticmethod
    def _append_lines(words_path: Path, words: list[str]) -> None:
        if not words:
            return
        try:
            words_path.parent.mkdir(parents=True, exist_ok=True)
            needs_leading_newline = False
            if words_path.exists() and words_path.stat().st_size > 0:
                with open(words_path, "rb") as f:
                    f.seek(-1, 2)
                    needs_leading_newline = f.read(1) != b"\n"

            payload = ("\n" if needs_leading_newline else "") + "\n".join(words)
            with open(words_path, "a", encoding="utf-8") as f:
                f.write(payload)
        except OSError as err:
            raise RuntimeError(f"Failed to append secrets to '{words_path}': {err}") from err

    def get_secrets(self) -> list[str]:
        if not self.words_path.exists():
            return []
        try:
            with open(self.words_path, "r", encoding="utf-8") as f:
                return [line.rstrip("\r\n") for line in f if line.rstrip("\r\n")]
        except OSError as err:
            raise RuntimeError(f"Failed to read secrets from '{self.words_path}': {err}") from err
        
    def get_secret(self) -> str:
        secrets = self.get_secrets()
        if not secrets:
            raise ValueError(f"No secrets available in '{self.words_path}'")
        return self.random.choice(secrets)           

    def count_secrets(self)->int:
        return len(self.get_secrets())

    def write_secret(self, word: str) -> None:
        if not isinstance(word, str) or not word.strip():
            raise ValueError("Secret word must be a non-empty string")
        self._append_lines(self.words_path, [word.strip().lower()])

    def load_secret(self) -> None:
        word = self.generator.getWord()
        self._append_lines(self.words_path, [word])

    def load_secrets(self) -> None:
        words = self.generator.getWords()
        self._append_lines(self.words_path, words)

    def clear_secrets(self) -> None:
        if self.words_path.exists():
            try:
                self.words_path.unlink()
            except OSError as err:
                raise RuntimeError(f"Failed to clear secrets file '{self.words_path}': {err}") from err