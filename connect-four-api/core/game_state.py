from enum import Enum
from asyncio import Event
from typing import Optional

from core.board import Board
from core.logger import logger
from core.constants import SELECTABLE_ALGORITHMS


class GameStatus(Enum):
    WAITING = "waiting"
    RUNNING = "running"
    ENDED = "ended"
    ERROR = "error"


class GameState:
    def __init__(self):
        self.status: GameStatus = GameStatus.WAITING
        self.board: Board = Board()
        self.control_event: Event = Event()
        self.current_algorithm: Optional[str] = None

    def start_game(
        self,
        algorithm: str = SELECTABLE_ALGORITHMS[0],
        algo_params: dict = {},
    ):
        logger.info(f"Starting game with algorithm: {algorithm}")
        logger.info(f"Starting algorithm with the following parameters: {algo_params}")
        self.status = GameStatus.RUNNING
        self.current_algorithm = algorithm
        self.current_depth = algo_params.get("minimax_depth", 8)
        self.current_sim = algo_params.get("mcts_sim", 20000)
        self.board.reset()
        self.control_event.clear()

    def end_game(self):
        self.status = GameStatus.ENDED
        self.control_event.set()

    def is_game_running(self) -> bool:
        return self.status == GameStatus.RUNNING and not self.control_event.is_set()
