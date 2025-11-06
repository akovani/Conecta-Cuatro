import sys

import pygame
import torch
from pygame.locals import QUIT, MOUSEBUTTONDOWN

from connect_four_environment import ConnectFourEnvironment
from alphazero_model import AlphaZeroModel
from mcts import MCTS

CELL_SIZE = 100
COLUMNS = 7
ROWS = 6
RADIUS = int(CELL_SIZE // 2 - 5)

COLOR_BG = (0, 0, 0)
COLOR_EMPTY = (200, 200, 200)
COLOR_P1 = (255, 0, 0)
COLOR_P2 = (255, 255, 0)
COLOR_TEXT = (255, 255, 255)


MODEL_PATH = "alphazero_connect_four.pt"
N_SIMULATIONS = 200
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_alphazero_model(model_path=MODEL_PATH, device=DEVICE):
    model = AlphaZeroModel().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model


def draw_board(screen, env):
    """
    Draws the current game board (env.board) on the Pygame surface.
    Top left = (0,0) in pixels.
    """
    for c in range(COLUMNS):
        for r in range(ROWS):
            x_pos = c * CELL_SIZE + CELL_SIZE // 2
            y_pos = r * CELL_SIZE + CELL_SIZE // 2 + CELL_SIZE

            if env.board[r][c] == 0:
                color = COLOR_EMPTY
            elif env.board[r][c] == 1:
                color = COLOR_P1
            else:
                color = COLOR_P2

            pygame.draw.circle(screen, color, (x_pos, y_pos), RADIUS)

    pygame.display.update()


def show_winner_text(screen, winner):
    """
    Zeigt einen Text an, der den Gewinner verkündet.
    winner = 1 (KI), 2 (Mensch) oder 0 (Unentschieden)
    """
    font = pygame.font.SysFont("Arial", 48, bold=True)
    if winner == 0:
        text_surface = font.render("Unentschieden!", True, COLOR_TEXT)
    elif winner == 1:
        text_surface = font.render("KI (Rot) gewinnt!", True, COLOR_TEXT)
    else:
        text_surface = font.render("Du (Gelb) gewinnst!", True, COLOR_TEXT)

    rect = text_surface.get_rect(center=(CELL_SIZE * COLUMNS // 2, CELL_SIZE // 2))
    screen.blit(text_surface, rect)
    pygame.display.update()


def ai_move(env, model):
    """
    Führt den Zug der KI durch:
    - MCTS initialisieren
    - Spalte mit den meisten Besuchszahlen wählen
    - Zug in env.step(action)
    """
    mcts = MCTS(env, model, n_simulations=N_SIMULATIONS, device=DEVICE)
    state = env.get_state()
    action_visits = mcts.search(state, env.current_player)
    if len(action_visits) == 0:
        return
    best_action = max(action_visits, key=action_visits.get)
    env.step(best_action)


def main():
    pygame.init()
    screen_width = COLUMNS * CELL_SIZE
    screen_height = (ROWS + 1) * CELL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Connect Four - Human vs. AlphaZero-AI")

    model = load_alphazero_model(MODEL_PATH, DEVICE)

    font = pygame.font.SysFont("Arial", 24)

    env = ConnectFourEnvironment()

    screen.fill(COLOR_BG)
    draw_board(screen, env)

    game_over = False

    if env.current_player == 1:
        ai_move(env, model)
        draw_board(screen, env)

    clock = pygame.time.Clock()

    while True:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if game_over:
                continue

            if event.type == MOUSEBUTTONDOWN and env.current_player == 2:
                x_pos = event.pos[0]
                col = x_pos // CELL_SIZE

                next_state, reward, done = env.step(col)

                draw_board(screen, env)

                if env.done:
                    game_over = True
                    show_winner_text(screen, env.winner)
                else:
                    ai_move(env, model)
                    draw_board(screen, env)
                    if env.done:
                        game_over = True
                        show_winner_text(screen, env.winner)

        screen.fill(COLOR_BG, (0, 0, screen_width, CELL_SIZE))  # Kopfzeile leeren
        if not game_over:
            if env.current_player == 2:
                text_surface = font.render("Du bist am Zug (Gelb)", True, COLOR_TEXT)
            else:
                text_surface = font.render("KI (Rot) ist am Zug...", True, COLOR_TEXT)
            screen.blit(text_surface, (10, 10))
            pygame.display.update()


if __name__ == "__main__":
    main()
