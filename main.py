import Environment as env
import Creation


#testing
game = env.sudoku()
Creation.generateRandom(game)
game.printBoard()
game.addNum(0,0,7)
print(Creation.validateInput(game))
game.printBoard()