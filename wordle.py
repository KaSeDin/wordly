import config
from history import History
from secrets import Secrets
from game import Game
import sys

class Wordle:

    def __init__(self):
        self.cfg=config.config
        self.history=History(self.cfg)
        self.secrets=Secrets(self.cfg)
        self.commands={
            "quit":self.cmd_quit,
            "help":self.cmd_help,
            "load_secrets":self.cmd_load_secrets,
            "new_game":self.cmd_start_game,
            "view_history":self.cmd_view_history
        }
        self.descriptions={
            "help":"Gives you list of commands that you can use outside game",
            "quit":"Quits from the game console",
            "load_secrets":"Load secrets into the dictionary for upcoming games",
            "new_game":"Start a new game",
            "view_history":"View your past performance"
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
        new_game=Game(new_secret,self.cfg,self.history)
        return True

    def cmd_view_history(self):
        hist=self.history.print_history()
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