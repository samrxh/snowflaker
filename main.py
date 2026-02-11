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

board = [
    [9, 9, 9, 7, 0, 7, 9, 9, 9],
    [7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0],
    [7, 0, 7, 0, 7, 0, 7, 0, 7],
    [0, 7, 0, 7, 0, 7, 0, 7, 0],
    [9, 9, 9, 0, 7, 0, 9, 9, 9]
]


# question: would it be better to make these nodes rather than a list? maybe
# if we need to know whether a cell is up or down whether it has a value or not, but do we?
# no, because if we determine that a path we are going down is impossible, we'll backtrack anyway

# okay, let's write the logic for verifying, starting with an up cell
def check_valid_number(board, row, col, num):
    # an up cell sees 2 left, 2 right, below and 2LR, and above and 1LR
    if board[row][col] == 7:
        # look 2 left
        for j in range(-2, 0):
            if col + j < 0:
                continue
            print(f"{row, col + j} = {board[row][col + j]}")
            if board[row][col+j] == num:
                return False

        # look 2 right
        for j in range(1, 3):
            if col + j > 8:
                continue
            print(f"{row, col + j} = {board[row][col + j]}")
            if board[row][col+j] == num:
                return False

        # look below, 2 left and 2 right
        for j in range(-2, 3):
            if row + 1 > 5 or 0 > col + j > 8:
                continue
            print(f"{row + 1, col + j} = {board[row + 1][col + j]}")
            if board[row+1][col+j] == num:
                return False

        # look above, 1 left and 1 right
        for j in range(-1, 2):
            if row - 1 < 0 or 0 > col + j > 8:
                continue
            print(f"{row - 1, col + j} = {board[row - 1][col + j]}")
            if board[row-1][col+j] == num:
                return False

        return True

    # a down cell sees 2 left, 2 right, below and 1LR, and above and 2LR
    elif board[row][col] == 0:
        # look 2 left
        for j in range(-2, 0):
            if col + j < 0:
                continue
            print(f"{row, col + j} = {board[row][col + j]}")
            if board[row][col+j] == num:
                return False

        # look 2 right
        for j in range(1, 3):
            if col + j > 8:
                continue
            print(f"{row, col + j} = {board[row][col + j]}")
            if board[row][col+j] == num:
                return False

        # look below, 1 left and 1 right
        for j in range(-1, 2):
            if row + 1 > 5 or 0 > col + j > 8:
                continue
            print(f"{row + 1, col + j} = {board[row + 1][col + j]}")
            if board[row+1][col+j] == num:
                return False

        # look above, 1 left and 1 right
        for j in range(-2, 3):
            if row - 1 < 0 or 0 > col + j > 8:
                continue
            print(f"{row - 1, col + j} = {board[row - 1][col + j]}")
            if board[row-1][col+j] == num:
                return False

        return True


# now that we have a checker, we can move forward with creating a solver
# the solver will check a number for a cell and see if it's valid
# if it's valid, go to the next unset cell
# if it's not valid, go to the next number up to 6
# if none are valid, backtrack


if __name__ == "__main__":
    print(check_valid_number(board, 0, 3, 1))
