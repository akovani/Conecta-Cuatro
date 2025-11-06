from typing import List

from asyncio import Event

# Path to the model file
MODEL_PATH = "agents/alphazero/alphazero_connect_four.pt"

# Connect Four Constants
ROWS = 6
COLUMNS = 7

# Global Board State (0 = empty, 1 = Player 1 (Human), 2 = Player 2 [Computer])
board_state: List[List[int]] = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

# Selectable Algorithms
SELECTABLE_ALGORITHMS = ["MiniMax", "MCTS", "AI_Mode"]

# AlphaZero Constants
ALPHAZERO_N_SIMULATIONS = 200

# Add game control event
game_control = Event()

# WebSocket Constants
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8000

# PLC Configuration
PLC_IP = "192.168.0.1"  # Replace with your actual PLC IP
PLC_RACK = 0
PLC_SLOT = 1
PLC_DB_NUMBER = 1

# MiniMax depth boundaries
MINIMAX_EASY_DEPTH = 2
MINIMAX_MEDIUM_DEPTH = 5
MINIMAX_HARD_DEPTH = 8

# MCTS simulation boundaries
MCTS_EASY_SIMULATIONS = 2000
MCTS_MEDIUM_SIMULATIONS = 10000
MCTS_HARD_SIMULATIONS = 20000

# MCTS exploration rate boundaries
MCTS_EASY_EXPLORATION = 1.2
MCTS_MEDIUM_EXPLORATION = 1.4
MCTS_HARD_EXPLORATION = 1.6

# Board state players

NO_GAME = 0
PLAYER_AI = 2
PLAYER_HUMAN = 1
