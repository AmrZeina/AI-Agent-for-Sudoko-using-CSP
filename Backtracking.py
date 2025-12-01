import Environment as env
import random

def backtrackingSearch(csp, Randomize = False):
    return backtracking(csp, csp, Randomize)

def backtracking(assignment, csp, Randomize):
    #1- Valid sudoku
    if assignment.isFilled():
        return assignment
    
    #2- Get first unassigned place
    rowIndex, colIndex = csp.getUnassigned()

    #3- Generate domain (copy)
    domain = set(env.DOMAIN)

    #Remove row numbers
    domain -= set(csp.getRow(rowIndex))

    #Remove column numbers
    domain -= set(csp.getCol(colIndex))

    #Remove square numbers
    domain -= set(csp.getSquare(rowIndex // 3, colIndex // 3))

    domain = list(domain)

    #Check for randomization
    if Randomize:
        random.shuffle(domain)

    #4- Try all domain values
    for val in domain:
        assignment.addNum(rowIndex, colIndex, val)

        result = backtracking(assignment, csp, Randomize)
        if result is not None:
            return result

        #Undo assignment
        assignment.addNum(rowIndex, colIndex, 0)

    return None