'''
Summary:
This is class which is mainly to hold the word and its score.
This is used as a helper for the ranking algorithm

Author:
Srivatsan Ananthakrishnan
'''
class RankedWord:
    
    
    def __init__(self,word,isPos,score=0, isUpper=False):
        self.score = score #holds the score/rank for the current word
        self.word = word # hold the word
        self.isPos = isPos #its a bool; this will be true, if the word is a phrase
        self.isUpper = isUpper; #its a bool; this will be true if the word is all in caps.

    def getscore(self): #method to return the score
        return self.score

    def getword(self): #method to return the current word
        return self.word

    def __lt__(self,other): #to sort
        return self.score < other.score

    def __str__(self): #to represent the class
        return str('Word : ' + str(self.word) + " Rank : " + str(self.score))
    

if __name__ == '__main__':
    print("This file can only be imported!")

