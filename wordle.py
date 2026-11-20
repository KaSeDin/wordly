import config as config
from history import History
from secrets import Secrets
from game import Game
from state import Result
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
            "stats":self.cmd_stats,
            "reset_stats":self.cmd_reset_stats,
            "rules":self.cmd_rules,
            "clear":self.cmd_clear,
        }
        self.descriptions={
            "help":"Gives you list of commands that you can use outside game",
            "quit":"Quits from the game console",
            "load_secrets":"Load secrets into the dictionary for upcoming games",
            "new_game":"Start a new game",
            "view_history":"View your past performance",
            "stats":"Show your game statistics",
            "reset_stats":"Clear saved games and statistics",
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

    def cmd_stats(self):
        games = [
            details
            for details in self.history.load_stats().values()
            if isinstance(details, dict)
        ]
        wins = sum(game.get("result") == Result.WIN.name for game in games)
        losses = sum(game.get("result") == Result.LOSS.name for game in games)
        guess_counts = []
        for game in games:
            guesses = game.get("guess", [])
            if not isinstance(guesses, list):
                guesses = []
            guess_count = game.get("guess_count")
            if not isinstance(guess_count, int) or isinstance(guess_count, bool) or guess_count < 0:
                guess_count = len(guesses)
            guess_counts.append(guess_count)

        games_played = len(games)
        win_rate = wins / games_played * 100 if games_played else 0
        average_guesses = (
            sum(guess_counts) / games_played if games_played else 0
        )

        print(f"Games played: {games_played}")
        print(f"Wins: {wins}")
        print(f"Losses: {losses}")
        print(f"Win rate: {win_rate:.1f}%")
        print(f"Average guesses: {average_guesses:.2f}")
        return True

    def cmd_reset_stats(self):
        confirmation = input(
            "Reset all saved games and statistics? Type 'yes' to confirm: "
        ).strip().lower()
        if confirmation != "yes":
            print("Reset cancelled.")
            return True

        self.history.save_stats({})
        print("Game history and statistics reset.")
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