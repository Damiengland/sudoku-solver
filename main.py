# Import modules
import pygame
import requests


# Initialize pygame font library
pygame.font.init()
# print(pygame.font.get_fonts())

# Fonts
FONT = pygame.font.SysFont('arial', 24)
GHOST_FONT = pygame.font.SysFont('arial', 12)


# Screen setup
WIDTH, HEIGHT = 600, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")
CLOCK = pygame.time.Clock()
FPS = 60
GRID_HEIGHT = HEIGHT - 60
GAP = GRID_HEIGHT // 9

# Colors
WHITE = (255, 255, 255)
OFF_WHITE = (232, 232, 232)
BLACK = (32, 32, 32)


# Sudoku grid API request
DIFFICULTY = ["easy", "medium", "hard"]

response = requests.get(url=f"https://sugoku.herokuapp.com/board?difficulty={DIFFICULTY[0]}")
response.raise_for_status()

board_numbers = response.json()["board"]
ghost_board_numbers = response.json()["board"]
# print(board_numbers)


class Box:
    def __init__(self, x, y, disabled):
        self.x = x
        self.y = y
        self.active = False
        self.ghost = False
        self.disabled = disabled

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x * GAP + 5, self.y * GAP + 5, GAP, GAP))


def get_clicked_pos(pos):
    x, y = pos

    row = x // GAP
    col = y // GAP
    return row, col


# Build sudoku grid
def build_grid(numbers):
    grid = []
    for x in range(9):
        arr = []
        for y in range(9):
            if numbers[y][x] == 0:
                arr.append(Box(x, y, False))
            else:
                arr.append(Box(x, y, True))
        grid.append(arr)
    return grid


def input_start_numbers(win, numbers):

    for row in range(9):
        for col in range(9):
            input_text = FONT.render(f"{str(numbers[row][col])}", True, BLACK)
            if numbers[row][col] != 0:
                win.blit(input_text, (col * GAP + GAP // 2, row * GAP + GAP // 2 - 7))


def valid(board, num, pos):

    # Check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_x * 3, box_x * 3 + 3):
        for j in range(box_y * 3, box_y * 3 + 3):
            if board[i][j] == num:
                return False

    # Check row
    for i in range(9):
        if board[pos[1]][i] == num:
            return False

    # Check col
    for i in range(9):
        if board[i][pos[0]] == num:
            return False

    return True


def get_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return i, j


def algorithm(board):

    find = get_empty(board)

    if not find:
        return True
    else:
        row, col = find

    for i in range(1, 10):
        # Visualize algorithm
        value = FONT.render(f"{str(i)}", True, BLACK)
        WIN.blit(value, (col * GAP + GAP // 2, row * GAP + GAP // 2 - 7))
        pygame.display.update()
        pygame.time.delay(10)

        if valid(board, i, (col, row)):
            board[row][col] = i

            if algorithm(board):
                return True

        board[row][col] = 0

        pygame.draw.rect(WIN, WHITE, (col * GAP + 10, row * GAP + 10, GAP - 10, GAP - 10))


def draw_grid(win):

    for row in range(10):
        if row % 3 == 0:
            pygame.draw.line(win, BLACK, (5, row * GAP + 5), (GRID_HEIGHT, row * GAP + 5), 5)
        else:
            pygame.draw.line(win, BLACK, (5, row * GAP + 5), (GRID_HEIGHT, row * GAP + 5))

    for col in range(10):
        if col % 3 == 0:
            pygame.draw.line(win, BLACK, (col * GAP + 5, 3), (col * GAP + 5, GRID_HEIGHT + 2), 5)
        else:
            pygame.draw.line(win, BLACK, (col * GAP + 5, 3), (col * GAP + 5, GRID_HEIGHT + 2))


def remove_active_select(grid):
    for row in range(9):
        for col in range(9):
            grid[row][col].active = False


def timer():
    current_time = pygame.time.get_ticks() // 1000
    minutes = current_time // 60
    seconds = current_time - (60 * minutes)
    if seconds < 10:
        seconds = f"0{seconds}"
    if minutes < 10:
        minutes = f"0{minutes}"
    return minutes, seconds


# Draw elements on screen
def draw(win, grid, inputs, time):
    win.fill(WHITE)

    for col in range(9):
        for row in range(9):
            box = grid[col][row]

            if box.active:
                box.draw(win, OFF_WHITE)

    input_start_numbers(win, board_numbers)

    for i in inputs:
        input_text = GHOST_FONT.render(f"{str(i['num'])}", True, BLACK)
        WIN.blit(input_text, (i["pos"][0] * GAP + 10, i["pos"][1] * GAP + 10))

    draw_grid(win)

    timer_text = FONT.render(f"{str(time[0])}:{str(time[1])}", True, BLACK)
    win.blit(timer_text, (525, 608))

    pygame.display.update()


# MAIN RUN FUNCTION
def main():

    run = True

    grid = build_grid(board_numbers)

    selected_box = None

    user_inputs = []

    while run:

        CLOCK.tick(FPS)

        minutes, seconds = timer()

        draw(WIN, grid, user_inputs, (minutes, seconds))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                selected_box = (row, col)
                # Try except - to handle if mouse clicks outside grid
                try:
                    box = grid[row][col]
                    if box.disabled:
                        remove_active_select(grid)

                    elif not box.disabled:
                        remove_active_select(grid)
                        box.active = True

                except IndexError:
                    remove_active_select(grid)

            if pygame.mouse.get_pressed()[2]:

                if selected_box is not None:
                    num = ghost_board_numbers[selected_box[1]][selected_box[0]]

                    if valid(board_numbers, num, selected_box):
                        board_numbers[selected_box[1]][selected_box[0]] = \
                            ghost_board_numbers[selected_box[1]][selected_box[0]]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    algorithm(board_numbers)
                else:
                    # Handle index error when using keypad input
                    try:
                        key = pygame.key.name(event.key)[1]
                        try:
                            key = int(key)
                        except ValueError:
                            print("Not a valid input")
                    except IndexError:
                        key = pygame.key.name(event.key)
                        try:
                            key = int(key)
                        except ValueError:
                            print("Not a valid input")

                    if type(key) == int:
                        for i in user_inputs:
                            if selected_box == i["pos"]:
                                user_inputs.remove(i)
                        if not grid[selected_box[0]][selected_box[1]].disabled:
                            user_inputs.append({
                                "num": key,
                                "pos": selected_box
                            })
                            ghost_board_numbers[selected_box[1]][selected_box[0]] = key

    pygame.quit()


main()
