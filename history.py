from dataclasses import asdict,dataclass
import json 
from pathlib import Path
from state import Result,State
from typing import Any
from enum import Enum
from datetime import datetime, timezone

    
class History:

    def __init__(self,cfg):
        self.history_path=cfg.history_file
        self._create_history()

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