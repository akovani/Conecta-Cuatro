import numpy as np

from core.constants import ROWS, COLUMNS
from core.logger import logger


class Board:
    def __init__(self):
        self.board = np.zeros((ROWS, COLUMNS), dtype=int)

    def reset(self):
        self.board = np.zeros((ROWS, COLUMNS), dtype=int)

    def add_pos_to_board(self, column: str, player: int = 1) -> bool:
        """
        Add coin for the given player to the global board state.

        :param column: Character between 'A' and 'G' that defines the column.
        :param player: Player that places the coin (Default human).
        :return: True, if coin placed successfully, otherwise False.
        """
        column = column.upper()

        if len(column) != 1 or column < "A" or column > "G":
            logger.error("Invalid column letter. Allowed are A to G.")
            return False

        col_index = ord(column) - ord("A")

        for row in reversed(range(ROWS)):
            if self.board[row][col_index] == 0:
                self.board[row][col_index] = player
                return True

        logger.error(f"Column {column} is full.")
        return False

    def winner_check(self) -> int:
        """
        Check if there is a winner in the current board state.

        :param board_state: Current board state.
        :return: 0 if no winner, 1 if player 1 wins, 2 if player 2 wins.
        """
        for r in range(ROWS):
            for c in range(COLUMNS):
                if self.board[r][c] == 0:
                    continue

                # Check horizontal
                if c + 3 < COLUMNS:
                    if (
                        self.board[r][c]
                        == self.board[r][c + 1]
                        == self.board[r][c + 2]
                        == self.board[r][c + 3]
                    ):
                        return self.board[r][c]

                # Check vertical
                if r + 3 < ROWS:
                    if (
                        self.board[r][c]
                        == self.board[r + 1][c]
                        == self.board[r + 2][c]
                        == self.board[r + 3][c]
                    ):
                        return self.board[r][c]

                # Check diagonal (top-left to bottom-right)
                if r + 3 < ROWS and c + 3 < COLUMNS:
                    if (
                        self.board[r][c]
                        == self.board[r + 1][c + 1]
                        == self.board[r + 2][c + 2]
                        == self.board[r + 3][c + 3]
                    ):
                        return self.board[r][c]

                # Check diagonal (bottom-left to top-right)
                if r - 3 >= 0 and c + 3 < COLUMNS:
                    if (
                        self.board[r][c]
                        == self.board[r - 1][c + 1]
                        == self.board[r - 2][c + 2]
                        == self.board[r - 3][c + 3]
                    ):
                        return self.board[r][c]

        return 0
