import random

class Secrets:

    def __init__(self,cfg):
        self.words_path=cfg.secrets_file
        self.random=random.Random()
        
    def __str__(self) -> str:
        return f"Secrets(words_path={self.words_path})"

    def _append_lines(self, words: list[str]) -> None:
        if not words:
            return
        self.words_path.parent.mkdir(parents=True, exist_ok=True)
        needs_leading_newline = False
        if self.words_path.exists() and self.words_path.stat().st_size > 0:
            with open(self.words_path, "rb") as f:
                f.seek(-1, 2)
                needs_leading_newline = f.read(1) != b"\n"

        payload = ("\n" if needs_leading_newline else "") + "\n".join(words)
        with open(self.words_path, "a", encoding="utf-8") as f:
            f.write(payload)

    def get_secrets(self)->list[str]:
        if not self.words_path.exists():
            return []
        with open(self.words_path, "r", encoding="utf-8") as f:
            return [line.rstrip("\r\n") for line in f if line.rstrip("\r\n")]
        
    def get_secret(self) -> str:
        secrets=self.get_secrets()
        if not secrets:
            raise ValueError("No secrets available")
        return self.random.choice(secrets)            

    def count_secrets(self)->int:
        return len(self.get_secrets())

    def write_secret(self, word: str) -> None:
        self._append_lines([word])

    def load_secret(self, generator) -> None:
        self._append_lines([generator.getWord()])

    def load_secrets(self, generator) -> None:
        self._append_lines(generator.getWords())

    def clear_secrets(self) -> None:
        if self.words_path.exists():
            self.words_path.unlink()
