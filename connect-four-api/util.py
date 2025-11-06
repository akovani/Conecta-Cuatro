import numpy as np
from typing import List
from core.constants import (
    MINIMAX_EASY_DEPTH,
    MINIMAX_MEDIUM_DEPTH,
    MINIMAX_HARD_DEPTH,
    MCTS_EASY_SIMULATIONS,
    MCTS_MEDIUM_SIMULATIONS,
    MCTS_HARD_SIMULATIONS,
    MCTS_EASY_EXPLORATION,
    MCTS_MEDIUM_EXPLORATION,
    MCTS_HARD_EXPLORATION,
)


def board_state_to_env_board(board_state: List[List[int]]) -> np.ndarray:
    """
    Convert the game's board_state to the environment's board format.

    Both use the same representation (0=empty, 1=player1, 2=player2),
    but different types (List[List[int]] vs np.ndarray).

    Args:
        board_state (List[List[int]]): The game's board state.

    Returns:
        np.ndarray: The environment's board format.
    """
    return np.array(board_state)


def env_board_to_board_state(env_board: np.ndarray) -> List[List[int]]:
    """
    Convert the environment's board to the game's board_state format.

    Args:
        env_board (np.ndarray): The environment's board.

    Returns:
        List[List[int]]: The game's board state format.
    """
    return env_board.tolist()


def get_algorithm_params(mode: str, difficulty: int) -> dict:
    """
    Map difficulty level (1-3) to algorithm-specific parameters.

    Args:
        mode: Algorithm mode ("MiniMax", "MCTS", or "AI_Mode")
        difficulty: Difficulty level (1=Easy, 2=Medium, 3=Hard)

    Returns:
        Dictionary containing algorithm-specific parameters
    """
    if difficulty not in [1, 2, 3]:
        raise ValueError("Difficulty must be between 1 and 3")

    match mode:
        case "MiniMax":
            depth_mapping = {
                1: MINIMAX_EASY_DEPTH,
                2: MINIMAX_MEDIUM_DEPTH,
                3: MINIMAX_HARD_DEPTH,
            }
            return {"minimax_depth": depth_mapping[difficulty]}

        case "MCTS":
            sim_mapping = {
                1: MCTS_EASY_SIMULATIONS,
                2: MCTS_MEDIUM_SIMULATIONS,
                3: MCTS_HARD_SIMULATIONS,
            }
            expl_mapping = {
                1: MCTS_EASY_EXPLORATION,
                2: MCTS_MEDIUM_EXPLORATION,
                3: MCTS_HARD_EXPLORATION,
            }
            return {
                "mcts_sim": sim_mapping[difficulty],
                "expl_rate": expl_mapping[difficulty],
            }

        case "AI_Mode":
            # AI Mode uses fixed parameters from training
            return {}

        case _:
            raise ValueError("Invalid mode")
