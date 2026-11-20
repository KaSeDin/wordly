import config as config
from history import History
from secrets import Secrets
from game import Game
import sys

class Wordle:

    def __init__(self):
        self.cfg=config.config
        self.history=History(self.cfg)
        self.secrets=Secrets(self.cfg)
        self.rules = {
            "Objective": "Guess the hidden word.",
            "Guess length": f"Each guess must be exactly {self.cfg.word_length} letters.",
            "Attempts": f"You have {self.cfg.max_guesses} guesses.",
            "Feedback": "Green is correct, yellow is in the word but misplaced, "
                        "and black is not in the word.",
            "In-game commands": "status, give_up, and back",
        }
        self.commands={
            "quit":self.cmd_quit,
            "help":self.cmd_help,
            "load_secrets":self.cmd_load_secrets,
            "new_game":self.cmd_start_game,
            "view_history":self.cmd_view_history,
            "rules":self.cmd_rules,
            "clear":self.cmd_clear,
        }
        self.descriptions={
            "help":"Gives you list of commands that you can use outside game",
            "quit":"Quits from the game console",
            "load_secrets":"Load secrets into the dictionary for upcoming games",
            "new_game":"Start a new game",
            "view_history":"View your past performance",
            "rules":"Show the game rules",
            "clear":"Clear the console",
        }

    def cmd_quit(self):
        print("Thanks for playing")
        sys.exit(0)
        return False

    def cmd_help(self):
        for key in self.descriptions:
            print(key," : ",self.descriptions[key])
        return True

    def cmd_load_secrets(self):
        self.secrets.load_secrets()
        return True

    def cmd_start_game(self):
        new_secret=self.secrets.get_secret()
        new_game=Game(new_secret,self.cfg,self.history,True)
        return True

    def cmd_view_history(self):
        hist=self.history.print_history()
        print(hist if hist else "No games played yet.")
        return True

    def cmd_rules(self):
        print("Wordle Rules:")
        for heading, description in self.rules.items():
            print(f"  {heading}: {description}")
        return True

    def cmd_clear(self):
        print("\033[2J\033[H", end="", flush=True)
        return True

    def execute(self,cmd)->bool:
        cmd=cmd.strip()
        if not cmd:
            return True
        
        action=self.commands.get(cmd)
        if action is None:
            return True
        return action()


    def run(self):
        print("Welcome! Type 'help' to see commands.")
        while True:
            try:
                user_line = input("\n> ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting game.")
                break
            if not self.execute(user_line):
                break



if __name__=="__main__":
    wordle=Wordle()
    wordle.run()