from typing import Optional, List
import torch

from core.constants import ALPHAZERO_N_SIMULATIONS
from agents.alphazero.connect_four_environment import ConnectFourEnvironment
from agents.alphazero.mcts import MCTS
from agents.alphazero.alphazero_model import AlphaZeroModel
from util import board_state_to_env_board

from core.constants import MODEL_PATH

# PyO3 imports
import minimax_algorithm
import monte_carlo_tree_search


class MoveCalculator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.alphazero_model = self._load_alphazero_model()
        self.env = ConnectFourEnvironment()

    def _load_alphazero_model(self) -> AlphaZeroModel:
        model = AlphaZeroModel().to(self.device)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
        model.eval()
        return model

    def get_best_move(
        self,
        board_state: List[List[int]],
        mode: str,
        minimax_depth: int,
        mcts_sim: int,
        expl_rate: float = 1.4,
    ) -> Optional[str]:
        """
        Calculate the best move based on the selected algorithm.

        Args:
            board_state: Current state of the board
            mode: Algorithm to use ("MiniMax", "MCTS", or "AI_Mode")

        Returns:
            Column letter (A-G) for the best move, or None if no valid move
        """
        match mode:
            case "MiniMax":
                return minimax_algorithm.get_best_move(board_state, minimax_depth)

            case "MCTS":
                return monte_carlo_tree_search.get_best_move_mcts(
                    board_state, mcts_sim, expl_rate
                )

            case "AI_Mode":
                return self._get_alphazero_move(board_state)

            case _:
                raise ValueError(
                    "Invalid mode. Please choose from: MiniMax, MCTS, AI_Mode"
                )

    def _get_alphazero_move(self, board_state: List[List[int]]) -> Optional[str]:
        """Calculate best move using AlphaZero model."""
        self.env.board = board_state_to_env_board(board_state)
        self.env.current_player = 2  # AI is always player 2

        mcts = MCTS(
            self.env,
            self.alphazero_model,
            n_simulations=ALPHAZERO_N_SIMULATIONS,
            device=self.device,
        )

        state = self.env.get_state()
        action_visits = mcts.search(state, self.env.current_player)

        if not action_visits:
            return None

        best_column = max(action_visits, key=action_visits.get)
        return chr(ord("A") + best_column)  # Convert column index to letter
