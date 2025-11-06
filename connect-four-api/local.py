import pygame
import sys
import numpy as np

# from minimax_algorithm import (
#     get_best_move,
# )
from monte_carlo_tree_search import (
    get_best_move_mcts,
)

ROWS = 6
COLS = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
DEPTH = 8
SIMULATIONS = 20000
EXPLORATION = 1.6

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

PLAYER = 1
AI = 2


def create_board():
    board = np.zeros((ROWS, COLS), dtype=int)
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[0][col] == 0


def get_next_open_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r
    return None


def winning_move(board, piece):
    for c in range(COLS - 3):
        for r in range(ROWS):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    for c in range(COLS):
        for r in range(ROWS - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True
    return False


def draw_board(screen, board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLS):
        for r in range(ROWS):
            piece = board[r][c]
            x_pos = int(c * SQUARESIZE + SQUARESIZE / 2)
            y_pos = int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)

            if piece == PLAYER:
                pygame.draw.circle(screen, RED, (x_pos, y_pos), RADIUS)
            elif piece == AI:
                pygame.draw.circle(screen, YELLOW, (x_pos, y_pos), RADIUS)

    pygame.display.update()


def column_from_char(c):
    return ord(c) - ord("A")


def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Connect 4 mit Minimax-AI")
    myfont = pygame.font.SysFont("monospace", 75)

    board = create_board()
    game_over = False
    turn = 0

    draw_board(screen, board)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0 and not game_over:
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                col = int(posx // SQUARESIZE)

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER)

                    if winning_move(board, PLAYER):
                        label = myfont.render("Du gewinnst!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn = 1
                    draw_board(screen, board)

        if turn == 1 and not game_over:
            py_board = board.tolist()
            # best_move_char = nn.get_best_ai_move(py_board)
            # best_move_char = get_best_move(py_board, DEPTH)
            best_move_char = get_best_move_mcts(py_board, SIMULATIONS, EXPLORATION)
            best_col = column_from_char(best_move_char)

            if is_valid_location(board, best_col):
                row = get_next_open_row(board, best_col)
                drop_piece(board, row, best_col, AI)

                if winning_move(board, AI):
                    label = myfont.render("AI gewinnt!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True

                turn = 0
                draw_board(screen, board)

        if game_over:
            pygame.display.update()
            pygame.time.wait(3000)


main()
