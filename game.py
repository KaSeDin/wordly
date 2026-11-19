from state import State,Result
from guessresult import GuessResult
import config
class Game:

    def __init__(self,secret:str,cfg):
        self.secret=secret
        self.cfg=cfg
        self.guess_count=0
        self.result=Result.UNFINISHED
        self.guesses=[]

    def make_guess(self,guess:str):
        if self.result!=Result.UNFINISHED:
            raise Exception("Create new Game")
        self.guess_count+=1
        guess_result=GuessResult(guess,self.secret)
        self.guesses.append(guess_result)
        if guess_result.state==State.MATCHED:
            self.result=Result.WIN
        elif self.guess_count>=self.cfg.max_guesses:
            self.result=Result.LOSS
        print(guess_result)

cfg=config.config
temp=Game("apple",cfg)
for i in range(cfg.max_guesses):
    guess=input("Enter your guess: ")
    temp.make_guess(guess)