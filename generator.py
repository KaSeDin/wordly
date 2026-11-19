from wonderwords import RandomWord

class Generator:

    def __init__(self,cfg):
        self.rw=RandomWord()
        self.size=cfg.word_length
        self.word_count=cfg.word_count

    def __str__(self)->str:
        return f"Generator(size={self.size}, word_count={self.word_count})"

    def getWord(self)->str:
        return self.rw.word(
            word_min_length=self.size,
            word_max_length=self.size,
            exclude_with_spaces=True
        )
    
    def getWords(self)->list[str]:
        list=[]
        for i in range(self.word_count):
            word=self.getWord()
            list.append(word)
        return list

