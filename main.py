# import Environment as env
# import Creation
# import ArcConsistency as AC

# #testing
# game = env.sudoku()
# Creation.generateRandom(game)
# game.printBoard()
# AC.AC3(game)
# game.printBoard()

import Environment as env
import Creation
import ArcConsistency as AC
import SolveAC as ACS
import Backtracking as BK

game = env.sudoku()
Creation.generateRandom(game)
print("\nInitial Board:")
game.printBoard()
# Step 1: Arc Consistency
ACS.enforceArcConsistency(game)
game.printBoard()
# Step 2: Backtracking (to finish solving)
print("\nRunning Backtracking...")
solution = BK.backtrackingSearch(game)
print("\nFinal Solved Board:")
solution.printBoard()

