from state import State,Result
from guessresult import GuessResult

class Game:

    def __init__(self,secret:str,cfg,history):
        self.secret=secret
        self.cfg=cfg
        self.guess_count=0
        self.result=Result.UNFINISHED
        self.guesses=[]
        self.history=history
        self.history.update_stats(self.secret,self)
        self._start_game()

    def _make_guess(self,guess:str):
        if self.result!=Result.UNFINISHED:
            raise Exception("Create new Game")
        self.guess_count+=1
        guess_result=GuessResult(guess,self.secret)
        self.guesses.append(guess_result)
        if guess_result.state==State.MATCHED:
            self.result=Result.WIN
        elif self.guess_count>=self.cfg.max_guesses:
            self.result=Result.LOSS
        self.history.update_stats(self.secret,self,guess_result)
        print(guess_result)

    def _start_game(self):
        for _ in range(self.cfg.max_guesses):
            new_guess=input().strip()
            self._make_guess(new_guess)