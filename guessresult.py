from state import State 
from outcome import Outcome,Symbol

class GuessResult:

    def __init__(self,guess:str,secret:str,state:State=State.NOT_STARTED):
        self.guess=guess
        self.state=state
        self.outcomes=[]
        self._eval_guess(secret,len(secret))

    def __str__(self):
        visual=""
        for outcome in self.outcomes:
            visual+=Symbol[outcome.name].value
        return visual

    def _eval_guess(self,secret:str,len:int):
        map=dict()
        match=True
        for i in range(len):
            if secret[i]==self.guess[i]:
                self.outcomes.append(Outcome.CORRECT)
            else:
                match=False
                self.outcomes.append(Outcome.ABSENT)
                if secret[i] in map:
                    map[secret[i]]+=1
                else:
                    map[secret[i]]=1
        if match:
            self.state=State.MATCHED
            return 
        else:
            self.state=State.UNMATCHED
        for i in range(len):
            if self.outcomes[i]==Outcome.CORRECT:
                continue
            if self.guess[i] in map:
                self.outcomes[i]=Outcome.PRESENT
                map[self.guess[i]]-=1
                if map[self.guess[i]]==0:
                    del map[self.guess[i]]