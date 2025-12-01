import Environment as env
import Creation
import ArcConsistency as AC

#testing
game = env.sudoku()
Creation.generateRandom(game)
game.printBoard()
AC.AC3(game)
game.printBoard()