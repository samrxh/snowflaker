from time import perf_counter
from copy import deepcopy

# the basic board can be row of 3, 4 rows of 9, row of 3
# set to 0 for null value

# board = [
#     [0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0]
# ]

# now how do we verify programmatically?
# an up cell sees 2 left, 2 right, below and 2LR, and above and 1LR
# a down cell sees 2 left, 2 right, below and 1LR, and above and 2LR
# so, just change the board to recognize 1) inaccessible cells and 2) up/down cells
# 9 represents inaccessible
# 0 represents down
# 7 represents up

default_board = [
    [9, 9, 9, 7, 0, 7, 9, 9, 9],
    [7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0],
    [7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0],
    [9, 9, 9, 0, 7, 0, 9, 9, 9]
]

default_big_board = [
    [9, 9, 9, 9, 9, 9, 7, 0, 7, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 7, 0, 7, 0, 7, 0, 7, 0, 7, 9, 9, 9],
    [7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0],
    [7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0],
    [7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0],
    [9, 9, 9, 0, 7, 0, 7, 0, 7, 0, 7, 0, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 0, 7, 0, 9, 9, 9, 9, 9, 9]
]


# question: would it be better to make these nodes rather than a list? maybe
# if we need to know whether a cell is up or down whether it has a value or not, but do we?
# no, because if we determine that a path we are going down is impossible, we'll backtrack anyway

# okay, let's write the logic for verifying, starting with an up cell
def check_valid_number(board, row, col, num):
    def is_conflict(r, c):
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            return board[r][c] == num
        return False

    # an up cell sees 2 left, 2 right, below and 2LR, and above and 1LR
    if board[row][col] == 7:
        # look 2 left and 2 right
        for j in [-2, -1, 1, 2]:
            if is_conflict(row, col + j):
                return False

        # look below, 2 left and 2 right
        for j in range(-2, 3):
            if is_conflict(row + 1, col + j):
                return False

        # look above, 1 left and 1 right
        for j in range(-1, 2):
            if is_conflict(row - 1, col + j):
                return False

    # a down cell sees 2 left, 2 right, below and 1LR, and above and 2LR
    elif board[row][col] == 0:
        # look 2 left and 2 right
        for j in [-2, -1, 1, 2]:
            if is_conflict(row, col + j):
                return False

        # look below, 1 left and 1 right
        for j in range(-1, 2):
            if is_conflict(row + 1, col + j):
                return False

        # look above, 1 left and 1 right
        for j in range(-2, 3):
            if is_conflict(row - 1, col + j):
                return False

    return True


# now that we have a checker, we can move forward with creating a solver
# the solver will check a number for a cell and see if it's valid
# if it's valid, go to the next unset cell
# if it's not valid, go to the next number up to 6
# if none are valid, backtrack
def solver(board, row=0, col=3):
    # base case, end of the puzzle
    if row == len(board) - 1 and col == len(board[0]) - 1:
        return True

    # out of bounds, go to next row
    if col == len(board[0]) - 1:
        row += 1
        col = 0

    # not an empty cell, move on
    if board[row][col] in [1, 2, 3, 4, 5, 6, 9]:
        return solver(board, row, col + 1)

    for i in range(1, 7):
        # try all the numbers recursively
        if check_valid_number(board, row, col, i):
            # we need to save the cell direction (up or down) to return to it if none of the numbers work out
            cell_direction = board[row][col]

            board[row][col] = i
            if solver(board, row, col + 1):
                return True

            # none of the numbers worked, reset cell
            board[row][col] = cell_direction

    return False


# claire had the thought that we should make it show us what numbers we got wrong when we make mistakes on a puzzle
# i'll make it so we can input a board easily without all the annoying clicking or pressing of keys
# have it go row by row, inputting the cells for the board when blank
# then have it go row by row inputting what has been written
# solver can take the first input and solve it, then compare the second input to the solution and spit out mistake cells
def new_board():
    # indicate whether the board is small or big
    size = None
    while size not in [1, 2]:
        size = int(input("Enter 1 for a small board, 2 for a big board: "))

    if size == 1:
        board = deepcopy(default_board)
    elif size == 2:
        board = deepcopy(default_big_board)

    print("Enter the values for each cell.")

    if size == 1:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 9:
                    continue
                if i in [0, 5]:
                    while True:
                        try:
                            cell = input(f"Cell {i + 1}, {j - 2}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except:
                            print("Invalid number. Try again.")
                else:
                    while True:
                        try:
                            cell = input(f"Cell {i + 1}, {j + 1}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except:
                            print("Invalid number. Try again.")

    if size == 2:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == 9:
                    continue
                if i in [0, 9]:
                    while True:
                        try:
                            cell = input(f"Cell {i + 1}, {j - 5}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except:
                            print("Invalid number. Try again.")
                elif i in [1, 8]:
                    while True:
                        try:
                            cell = input(f"Cell {i + 1}, {j - 2}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except:
                            print("Invalid number. Try again.")
                else:
                    while True:
                        try:
                            cell = input(f"Cell {i + 1}, {j + 1}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except:
                            print("Invalid number. Try again.")

    return board


# now that we have a solver we can create a generator
# it may be helpful to consider how many possible puzzles there are as well as how many given cells are needed
# to first generate a puzzle, we can set that number of given cells in random locations
# try to solve it to check that it's a valid puzzle
# looking at the example puzzle it does look like given numbers follow a pattern wrt location


if __name__ == "__main__":

    test_board = [
        [9, 9, 9, 2, 0, 6, 9, 9, 9],
        [1, 0, 7, 0, 7, 0, 7, 0, 2],
        [0, 7, 0, 5, 0, 1, 0, 7, 0],
        [3, 0, 7, 0, 4, 0, 7, 0, 3],
        [0, 6, 0, 7, 0, 7, 0, 5, 0],
        [9, 9, 9, 0, 4, 0, 9, 9, 9]
    ]

    test_big_board = [
        [9, 9, 9, 9, 9, 9, 7, 2, 7, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 7, 1, 7, 0, 7, 0, 7, 2, 7, 9, 9, 9],
        [6, 0, 7, 0, 6, 0, 7, 3, 7, 0, 5, 0, 7, 0, 4],
        [0, 7, 0, 1, 0, 7, 0, 7, 0, 7, 0, 4, 0, 7, 0],
        [7, 6, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 6, 7],
        [0, 3, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 3, 0],
        [7, 0, 7, 6, 7, 0, 7, 0, 7, 0, 7, 5, 7, 0, 7],
        [1, 7, 0, 7, 3, 7, 0, 2, 0, 7, 3, 7, 0, 7, 3],
        [9, 9, 9, 0, 6, 0, 7, 0, 7, 0, 2, 0, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 0, 5, 0, 9, 9, 9, 9, 9, 9]
    ]

    begin = perf_counter()
    valid = solver(test_big_board)
    end = perf_counter()

    if valid:
        for line in test_big_board:
            print(" ".join(str(x) if x != 9 else " " for x in line))
    else:
        print("Board is invalid, unsolvable.")

    print(f"\nCompleted in {end - begin} seconds.")
