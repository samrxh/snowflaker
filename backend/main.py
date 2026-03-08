import json
from time import perf_counter
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
SAVED_BOARDS_DIR = BASE_DIR / "saved_boards"
SAVED_BOARDS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


small_grid = deepcopy(default_board)
big_grid = deepcopy(default_big_board)


@app.get("/board")
async def get_board(size: str = "small"):
    if size == "small":
        grid = small_grid
    elif size == "big":
        grid = big_grid
    else:
        grid = small_grid
    return {"grid": grid}

@app.post("/update")
async def update_cell(row: int, col: int, value: int, size: str = "small"):
    if size == "big":
        grid = big_grid
    else:
        grid = small_grid
    grid[row][col] = value
    return {"grid": grid}

@app.post("/save-board")
async def save_board(board: list[list[int]]):
    path = save_board_to_file(board)
    return {"path": path}
    
    
def check_valid_number(board, row, col, num, cell_state):
    def is_conflict(r, c):
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            return board[r][c] == num
        return False

    # an up cell sees 2 left, 2 right, below and 2LR, and above and 1LR
    if cell_state == 7:
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
    elif cell_state == 0:
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


# this will scan the board for an empty cell with the fewest possible valid numbers and then start with solving that
def solver(board):
    best_r, best_c, best_state = -1, -1, None
    min_options = 10

    # find the empty cell with the fewest possible valid numbers
    for r in range(len(board)):
        for c in range(len(board[0])):
            state = board[r][c]

            # If it's an empty cell (0 or 7)
            if state in [0, 7]:
                valid_count = 0

                # Count how many numbers can legally fit here
                for i in range(1, 7):
                    if check_valid_number(board, r, c, i, state):
                        valid_count += 1

                # If this cell has fewer options than our previous best, save it
                if valid_count < min_options:
                    min_options = valid_count
                    best_r, best_c, best_state = r, c, state

                # Early optimizations
                if min_options == 0:
                    return False  # Dead end! A cell has 0 possible moves, backtrack immediately.
                if min_options == 1:
                    break  # We found a cell with only 1 valid move, stop searching.

        if min_options == 1:
            break

    # 2. Base Case: If we never updated min_options, no empty cells are left!
    if min_options == 10:
        return True

    # 3. Try solving the best cell we found
    for i in range(1, 7):
        if check_valid_number(board, best_r, best_c, i, best_state):
            board[best_r][best_c] = i

            # Recursively try to solve the rest of the board
            if solver(board):
                return True

            # It didn't work out, reset the cell state and try the next number
            board[best_r][best_c] = best_state

    return False


def new_board(board=None):
    # indicate whether the board is small or big
    size = None

    if board is None:
        while size not in [1, 2]:
            try:
                size = int(input("Enter 1 for a small board, 2 for a big board: "))
            except ValueError:
                print("Choose 1 or 2.")
        if size == 1:
            board = deepcopy(default_board)
        elif size == 2:
            board = deepcopy(default_big_board)
    else:
        if len(board) == 6:
            size = 1
        else:
            size = 2

    print("Enter the values for each cell.")

    if size == 1:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] in [1, 2, 3, 4, 5, 6, 9]:
                    continue
                if i in [0, 5]:
                    while True:
                        try:
                            cell = input(f"Cell {cell_locator(size, i, j)}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except ValueError:
                            print("Invalid number. Try again.")
                else:
                    while True:
                        try:
                            print(size, i, j)
                            cell = input(f"Cell {cell_locator(size, i, j)}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except ValueError:
                            print("Invalid number. Try again.")

    if size == 2:
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] in [1, 2, 3, 4, 5, 6, 9]:
                    continue
                if i in [0, 9]:
                    while True:
                        try:
                            cell = input(f"Cell {cell_locator(size, i, j)}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except ValueError:
                            print("Invalid number. Try again.")
                elif i in [1, 8]:
                    while True:
                        try:
                            cell = input(f"Cell {cell_locator(size, i, j)}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except ValueError:
                            print("Invalid number. Try again.")
                else:
                    while True:
                        try:
                            cell = input(f"Cell {cell_locator(size, i, j)}: ")
                            if cell == "":
                                break
                            cell = int(cell)
                            if cell not in range(1, 7):
                                continue
                            board[i][j] = cell
                            break
                        except ValueError:
                            print("Invalid number. Try again.")

    return board


def find_mistakes(original_board=None, incorrect_board=None):
    if original_board is None:
        print("Input the board with only the original digits, pressing enter to skip a cell:")
        original_board = new_board()

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    original_board_path = f"{timestamp}-ORIGINAL"
    with open(original_board_path, 'w') as file:
        file.write(board_string(original_board))

    if len(original_board) == 6:
        size = 1
    else:
        size = 2

    if incorrect_board is None:
        print("Input the board with what you have entered:")
        incorrect_board = new_board(deepcopy(original_board))

    solved_board = deepcopy(original_board)
    valid = solver(solved_board)
    if not valid:
        print("Original board is invalid, check that you have entered it correctly.")
        exit()
    solved_board_path = f"{timestamp}-SOLUTION"
    with open(solved_board_path, 'w') as file:
        file.write(board_string(solved_board))

    for i in range(len(incorrect_board)):
        for j in range(len(incorrect_board[0])):
            # skip over empty cells, we know these aren't correct yet
            if incorrect_board[i][j] in [0, 7]:
                continue
            elif incorrect_board[i][j] != solved_board[i][j]:
                print(f"Cell at {cell_locator(size, i, j)} is not {incorrect_board[i][j]}.")


# i want to move the location info for cells into its own function
def cell_locator(size, row, col):
    x = row + 1
    y = col + 1
    if size == 1:
        if row == 0 or row == 5:
            y = col - 2
    elif size == 2:
        if row == 0 or row == 9:
            y = col - 5
        elif row == 1 or row == 8:
            y = col - 2
    return x, y


# i want to move the board printing and file saving to their own functions
# really need to make the board its own object with these methods at this point
def board_string(board):
    output = ""
    for line in board:
        row = " ".join(str(x) if x != 9 else " " for x in line) + "\n"
        output += row
    return output

def save_board_to_file(board):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    path = SAVED_BOARDS_DIR / f"{timestamp}-BOARD.json"
    with path.open('w', encoding='utf-8') as file:
        json.dump(board, file)
    return str(path)

# now that we have a solver we can create a generator
# it may be helpful to consider how many possible puzzles there are as well as how many given cells are needed
# to first generate a puzzle, we can set that number of given cells in random locations
# try to solve it to check that it's a valid puzzle
# looking at the example puzzle it does look like given numbers follow a pattern wrt location
