from dataclasses import asdict,dataclass
import json 
from pathlib import Path
from state import Result,State
from typing import Any
from enum import Enum
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

    
class History:

    def __init__(self,cfg):
        self.history_path=cfg.history_file
        self._create_history()
        self.tz_name="Asia/Kolkata"
        self.target_tz=ZoneInfo(self.tz_name)

    def _format_time(self,iso_str: str) -> str:
        dt = datetime.fromisoformat(iso_str).astimezone(self.target_tz)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    def _create_history(self):
        self.history_path.parent.mkdir(parents=True,exist_ok=True)
        if not self.history_path.exists():
            self.save_stats({})

    def _get_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()
    
    def save_stats(self,data:dict):
        with open(self.history_path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2)

    def load_stats(self):
        if not self.history_path.exists():
            return {}
        with open(self.history_path,"r",encoding="utf-8") as f:
            return json.load(f)

    def update_stats(self,key:str,game,new_guess=None):
        data=self.load_stats()
        entry = data.setdefault(key, {"guess": [],"started_at":self._get_timestamp()})
        if game is not None:
            entry["secret"] = game.secret
            entry["guess_count"]=game.guess_count
            entry["result"]=game.result.name
        guesses = entry.setdefault("guess", [])
        if new_guess is not None:
            guess_dict = {
                "guess": new_guess.guess,
                "state": str(new_guess.state.name),
                "outcomes": str(new_guess),
                "guessed_at":self._get_timestamp()
            }
            guesses.append(guess_dict)
        self.save_stats(data)

    def _format_game_report(self,data: dict|str) -> str:
        if isinstance(data, str):
            data = json.loads(data)
        lines: list[str] = []

        for game_id, details in data.items():
            lines.append(f"Game: {game_id}")
            lines.append(f"  Secret: {details['secret']}")
            lines.append(f"  Result: {details['result']} (Guesses: {details['guess_count']})")
            lines.append(f"  Started At: {self._format_time(details['started_at'])}")
            lines.append("  Guesses:")
            for i, g in enumerate(details["guess"], start=1):
                lines.append(
                    f"    {i}. {g['guess']} | {g['outcomes']} | {g['state']} | {self._format_time(g['guessed_at'])}"
                )

        return "\n".join(lines)

    def print_history(self):
        history=self.load_stats()
        print(self._format_game_report(history))