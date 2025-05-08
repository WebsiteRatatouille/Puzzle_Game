import model

puzzle = model.Puzzle()
print("initial state")
print(puzzle)
print("Solved?", puzzle.checkWin())
input("Press enter")

puzzle.shuffle()
print("Shuffled...")
print(puzzle)
print("Solved?", puzzle.checkWin())
input("Press enter")

puzzle.move(puzzle.LEFT)
print("Moving left...")
print(puzzle)
input("Press enter")

puzzle.move(puzzle.RIGHT)
print("Moving right...")
print(puzzle)
input("Press enter")

puzzle.move(puzzle.UP)
print("Moving up...")
print(puzzle)
input("Press enter")

puzzle.move(puzzle.DOWN)
puzzle.move(puzzle.DOWN)
puzzle.move(puzzle.DOWN)
puzzle.move(puzzle.DOWN)
print("Moving down x4...")
print(puzzle)
input("Press enter")

puzzle3 = model.Puzzle(3)
print("3x3 puzzle")
print(puzzle3)