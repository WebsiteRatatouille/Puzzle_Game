from random import choice

class Puzzle:
    
    UP = (1,0)
    DOWN = (-1,0)
    LEFT = (0,1)
    RIGHT = (0,-1)
    
    DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
    
    def __init__(self, boardSize = 4):
        self.boardSize = boardSize
        self.board = [[0]*boardSize for i in range(boardSize)]
        self.blankPos = (boardSize-1, boardSize-1)
        
        for i in range(boardSize):
            for j in range(boardSize):
                self.board[i][j] = i * boardSize + j + 1
            
        # 0 represents blank square, init in bottom right corner of board
        self.board[self.blankPos[0]][self.blankPos[1]] = 0
       
        
        self.shuffle()
    
    
    def __str__(self):
        outStr = ''
        for i in self.board:
            outStr += '\t'.join(map(str,i))
            outStr += '\n'
        return outStr
    
    
    def __getitem__(self, key):
        return self.board[key]
    
    
    def shuffle(self):
        nShuffles = 1000
        
        for i in range(nShuffles):
            dir = choice(self.DIRECTIONS)
            self.move(dir)
    
    
    def move(self, dir):
        newBlackPos = (self.blankPos[0] + dir[0], self.blankPos[1] + dir[1])
        
        if (newBlackPos[0] < 0 or newBlackPos[0] >= self.boardSize 
            or newBlackPos[1] < 0 or newBlackPos[1] >= self.boardSize
        ):
            return False
        
        self.board[self.blankPos[0]][self.blankPos[1]] = self.board[newBlackPos[0]][newBlackPos[1]]
        self.board[newBlackPos[0]][newBlackPos[1]] = 0
        self.blankPos = newBlackPos
        return True
            
    
    def checkWin(self):
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.board[i][j] != i * self.boardSize + j + 1 and self.board[i][j] != 0:
                    return False
        
        return True