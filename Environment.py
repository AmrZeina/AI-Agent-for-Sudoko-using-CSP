N = 9 #Grid Size
S = 3 #Sqiare Size
DOMAIN = [1,2,3,4,5,6,7,8,9]

class sudoku ():
    """
    Sudoku game class:
    Board representation: list of lists
    """
    def __init__(self):
        self.board = [[0 for _ in range(N)] for _ in range(N)]

    #Testing purposes
    def printBoard(self):
        for row in self.board:
            print(*row)

    def isFilled(self):
        for r in range (N):
            for c in range (N):
                if self.board[r][c] ==0:
                    return False
        return True
    
    def getUnassigned(self):
        """
        Get first value not assigned
        from left to right
        up to down
        """
        for r in range (N):
            for c in range (N):
                if self.board[r][c] ==0:
                    return r,c
    
    def getAllUnassigned(self):
        """
        Get all values not assigned
        from left to right
        up to down
        """
        unassigned = set()
        for r in range (N):
            for c in range (N):
                if self.board[r][c] ==0:
                    unassigned.add((r,c))
                
        return unassigned
    
    def getBoard(self):
        return self.board
    
    def getRow(self,row):
        return self.board[row]
    
    def getCol(self,col):
        col = [row[col] for row in self.board]
        return col

    def getSquare(self, startingRow, startingCol):
        square = []
        for r in range(startingRow * S , startingRow*S + S):
            for c in range(startingCol * S , startingCol*S + S):
                square.append(self.board[r][c])
        return square
    
    def addNum(self, row, col, value):
        self.board[row][col] = value