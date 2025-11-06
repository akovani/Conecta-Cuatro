import numpy as np


class ConnectFourEnvironment:
    """
    A simple environment class for a 6x7 Connect Four game.
    Player 1 = 1
    Player 2 = 2
    Empty Field = 0
    """

    ROWS = 6
    COLS = 7

    def __init__(self):
        self.reset()

    def reset(self):
        self.board = np.zeros((self.ROWS, self.COLS), dtype=int)
        self.current_player = 1
        self.done = False
        self.winner = None
        return self.get_state()

    def get_state(self):
        """Returns a copy of the current state of the board."""
        return self.board.copy()

    def step(self, action_col):
        """
        Perform an action in the environment.
        """
        if self.done:
            return self.get_state(), 0, True

        if not self.is_valid_action(action_col):
            return self.get_state(), -10, True

        row = self.get_next_open_row(action_col)
        self.board[row][action_col] = self.current_player

        if self.check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player
            reward = 1
        elif self.check_draw():
            self.done = True
            self.winner = 0
            reward = 0
        else:
            reward = 0

        self.current_player = 2 if self.current_player == 1 else 1

        return self.get_state(), reward, self.done

    def is_valid_action(self, col):
        return self.board[0][col] == 0

    def get_valid_actions(self):
        valid_actions = []
        for c in range(self.COLS):
            if self.is_valid_action(c):
                valid_actions.append(c)
        return valid_actions

    def get_next_open_row(self, col):
        for r in range(self.ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return None

    def check_winner(self, player):
        board = self.board
        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if (
                    board[r][c] == player
                    and board[r][c + 1] == player
                    and board[r][c + 2] == player
                    and board[r][c + 3] == player
                ):
                    return True
        # Vertikal
        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if (
                    board[r][c] == player
                    and board[r + 1][c] == player
                    and board[r + 2][c] == player
                    and board[r + 3][c] == player
                ):
                    return True
        # Diagonal (positiv)
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if (
                    board[r][c] == player
                    and board[r + 1][c + 1] == player
                    and board[r + 2][c + 2] == player
                    and board[r + 3][c + 3] == player
                ):
                    return True
        # Diagonal (negativ)
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if (
                    board[r][c] == player
                    and board[r - 1][c + 1] == player
                    and board[r - 2][c + 2] == player
                    and board[r - 3][c + 3] == player
                ):
                    return True

        return False

    def check_draw(self):
        return np.all(self.board != 0)
