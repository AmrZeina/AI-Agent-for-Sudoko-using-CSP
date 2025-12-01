import Backtracking as bk
import Environment as env
import random
import copy

def copyBoard(board):
    """
    Returns a deep copy of the Sudoku object
    """
    new_board = env.sudoku()
    new_board.board = copy.deepcopy(board.getBoard())
    return new_board

def generateRandom(input):
    """
    Function go solve empty board using backtracking and then remove parts of the solution
    in order to make it valid board
    """
    fullBoard = bk.backtrackingSearch(input, Randomize= True)
    if fullBoard is not None:
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        for i in range(50): #50 cells to be removed
            r, c = cells[i]
            input.addNum(r, c, 0)
 
def validateInput(input):
    """
    Function go solve a copy from the input, and if solved, then it is valid
    """
    newBoard = copyBoard(input)
    if bk.backtrackingSearch(newBoard) is not None:
        return True
    else:
        return False