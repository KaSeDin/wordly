from dataclasses import field,dataclass
import json 
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from validators import validate_non_empty_path,validate_not_none,validate_isinstance

@dataclass
class History:
    cfg:Any
    tz_name:str=field(default="Asia/Kolkata",repr=False)

    def __post_init__(self) -> None:
        validate_not_none("cfg", self.cfg)
        validate_non_empty_path("cfg.history_file", self.cfg.history_file)
        validate_isinstance("tz_name",self.tz_name,str)
        if not self.tz_name.strip():
            raise ValueError("tz_name must be a non-empty timezone string")
        try:
            ZoneInfo(self.tz_name)
        except ZoneInfoNotFoundError as err:
            raise ValueError(f"Invalid timezone name: {self.tz_name!r}") from err

        self._create_history(self.history_path)

    @property
    def history_path(self) -> Path:
        return self.cfg.history_file

    def __str__(self) -> str:
        return f"History(history_path={self.history_path}, tz_name={self.tz_name!r})"

    @classmethod
    def from_config(cls, cfg: Any, tz_name: str = "Asia/Kolkata") -> "History":
        return cls(cfg=cfg, tz_name=tz_name)

    @staticmethod
    def _format_time(iso_str: str, tz_name: str = "Asia/Kolkata") -> str:
        try:
            target_tz = ZoneInfo(tz_name)
            dt = datetime.fromisoformat(iso_str).astimezone(target_tz)
            return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        except (ValueError, TypeError, ZoneInfoNotFoundError) as err:
            raise RuntimeError(
                f"Failed to format timestamp {iso_str!r} for timezone {tz_name!r}: {err}"
            ) from err
        
    @staticmethod
    def _create_history(history_file) -> None:
        try:
            history_file.parent.mkdir(parents=True, exist_ok=True)
            if not history_file.exists():
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2)
        except (OSError, TypeError) as err:
            raise RuntimeError(
                f"Failed to initialize history file '{history_file}': {err}"
            ) from err

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def save_stats(self, data: dict[str, Any]) -> None:
        validate_isinstance("data",data,dict)
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (OSError, TypeError) as err:
            raise RuntimeError(
                f"Failed to save history to '{self.history_path}': {err}"
            ) from err

    def load_stats(self) -> dict[str, Any]:
        if not self.history_path.exists():
            return {}
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, json.JSONDecodeError) as err:
            raise RuntimeError(
                f"Failed to load history from '{self.history_path}': {err}"
            ) from err

        validate_isinstance("loaded",loaded,dict)
        return loaded

    def update_stats(self, key: str, game: Any, new_guess: Any = None) -> None:
        validate_isinstance("key",key,str)
        if not key.strip():
            raise ValueError("Game key must be a non-empty string")

        data = self.load_stats()
        entry = data.setdefault(
            key, {"guess": [], "started_at": self._get_timestamp()}
        )

        if game is not None:
            try:
                entry["secret"] = game.secret
                entry["guess_count"] = game.guess_count
                entry["result"] = game.result.name
            except AttributeError as err:
                raise RuntimeError(f"Game object missing expected attribute: {err}") from err

        guesses = entry.setdefault("guess", [])
        if new_guess is not None:
            try:
                guess_dict = {
                    "guess": new_guess.guess,
                    "state": str(new_guess.state.name),
                    "outcomes": str(new_guess),
                    "guessed_at": self._get_timestamp(),
                }
            except AttributeError as err:
                raise RuntimeError(
                    f"Guess object missing expected attribute: {err}"
                ) from err
            guesses.append(guess_dict)

        self.save_stats(data)

    @staticmethod
    def _format_game_report(
        data: dict[str, Any] | str,
        tz_name: str = "Asia/Kolkata",
    ) -> str:
        try:
            if isinstance(data, str):
                data = json.loads(data)
            validate_isinstance("data",data,dict)

            lines: list[str] = []
            for game_id, details in data.items():
                if not isinstance(details, dict):
                    continue
                secret = details.get("secret", "N/A")
                result = details.get("result", "IN_PROGRESS")
                guess_count = details.get("guess_count", len(details.get("guess", [])))
                started_at = details.get("started_at")
                formatted_start = (
                    History._format_time(started_at, tz_name) if started_at else "N/A"
                )

                lines.append(f"Game: {game_id}")
                lines.append(f"  Secret: {secret}")
                lines.append(f"  Result: {result} (Guesses: {guess_count})")
                lines.append(f"  Started At: {formatted_start}")
                lines.append("  Guesses:")

                for i, g in enumerate(details.get("guess", []), start=1):
                    guessed_at = g.get("guessed_at")
                    formatted_guess_time = (
                        History._format_time(guessed_at, tz_name) if guessed_at else "N/A"
                    )
                    lines.append(
                        f"    {i}. {g.get('guess')} | {g.get('outcomes')} | "
                        f"{g.get('state')} | {formatted_guess_time}"
                    )

            return "\n".join(lines)
        except RuntimeError:
            raise
        except (json.JSONDecodeError, TypeError, ValueError) as err:
            raise RuntimeError(f"Failed to format game history report: {err}") from err

    def print_history(self) -> str:
        history = self.load_stats()
        report = self._format_game_report(history, self.tz_name)
        return report