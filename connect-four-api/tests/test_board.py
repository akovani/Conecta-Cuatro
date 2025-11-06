import pytest
import numpy as np

from core.board import Board
from core.constants import ROWS, COLUMNS


@pytest.fixture
def board_instance():
    """
    Returns a fresh instance of the Board class.
    """
    return Board()


def test_board_initialization(board_instance):
    """
    Test that on initialization, the board is a numpy array of zeros with correct shape.
    """
    assert isinstance(board_instance.board, np.ndarray)
    assert board_instance.board.shape == (ROWS, COLUMNS)
    assert np.count_nonzero(board_instance.board) == 0


def test_board_reset(board_instance):
    """
    Test that reset() clears the board to all zeros.
    """
    # Place a coin
    board_instance.board[0, 0] = 1
    board_instance.reset()
    assert np.count_nonzero(board_instance.board) == 0, (
        "Board should be cleared after reset."
    )


@pytest.mark.parametrize("column", ["A", "D", "G"])
def test_add_pos_to_board_valid_columns(board_instance, column):
    """
    Test adding a piece to valid columns.
    """
    placed = board_instance.add_pos_to_board(column, player=1)
    assert placed is True, f"Should successfully place a coin in column {column}."

    col_index = ord(column) - ord("A")
    # Should land in the bottom row (ROWS - 1)
    assert board_instance.board[ROWS - 1, col_index] == 1, (
        f"Bottom cell in column {column} should have player 1's coin."
    )


@pytest.mark.parametrize("column", ["", "H", "Z", "!", "1", "AB"])
def test_add_pos_to_board_invalid_columns(board_instance, column, caplog):
    """
    Test that adding a piece to invalid column letters fails and logs an error.
    """
    placed = board_instance.add_pos_to_board(column, player=1)
    assert placed is False, f"Should fail to place a coin in invalid column {column}."

    # Check for log message
    assert any("Invalid column letter" in rec.message for rec in caplog.records), (
        "Expected a log error about invalid column letter."
    )


def test_add_pos_to_board_column_full(board_instance, caplog):
    """
    Fill up a column completely, then ensure a subsequent placement returns False and logs an error.
    """
    # Fill column "A" with ROWS coins
    for _ in range(ROWS):
        assert board_instance.add_pos_to_board("A", player=1) is True

    # Now column A is full; next attempt must fail
    assert board_instance.add_pos_to_board("A", player=1) is False, (
        "Placing an 7th coin in a 6-row board should fail."
    )
    assert any("Column A is full." in rec.message for rec in caplog.records), (
        "Expected a log error about full column."
    )


def test_winner_check_no_winner(board_instance):
    """
    If the board is empty or has a few coins without 4 in a row, winner_check should return 0.
    """
    # Place some coins but no connect-4
    board_instance.add_pos_to_board("A", 1)
    board_instance.add_pos_to_board("B", 2)
    board_instance.add_pos_to_board("C", 1)
    board_instance.add_pos_to_board("D", 2)

    assert board_instance.winner_check() == 0, "No winner yet."


def test_winner_check_horizontal(board_instance):
    """
    Test for a horizontal connect-4.
    """
    # Place 4 player1 coins in row 5 (bottom row) from col A to D
    for col in ["A", "B", "C", "D"]:
        board_instance.add_pos_to_board(col, 1)
    assert board_instance.winner_check() == 1, "Player 1 should have a horizontal win."


def test_winner_check_vertical(board_instance):
    """
    Test for a vertical connect-4.
    """
    col = "C"
    for _ in range(4):
        board_instance.add_pos_to_board(col, 2)
    assert board_instance.winner_check() == 2, "Player 2 should have a vertical win."


def test_winner_check_diagonal_top_left_to_bottom_right(board_instance):
    """
    Test a diagonal win (top-left to bottom-right).
    For example:
       Row2 ColA -> Row3 ColB -> Row4 ColC -> Row5 ColD (all player1)
    """
    # We need to 'stack' some pieces so that we can place coins in an actual diagonal.
    # The simplest approach: fill empty spaces in columns so that the next coin lands
    # at the desired row for each step.

    # Step 1: place coin in "A" (bottom row = row 5)
    board_instance.add_pos_to_board("A", 1)
    # Step 2: place coin in "B" for the bottom row, then again in "B" for row 4
    board_instance.add_pos_to_board("B", 2)  # filler
    board_instance.add_pos_to_board("B", 1)  # desired position at row 4
    # Step 3: place coin in "C" for bottom row, then row 4, then row 3
    board_instance.add_pos_to_board("C", 2)  # filler
    board_instance.add_pos_to_board("C", 2)  # filler
    board_instance.add_pos_to_board("C", 1)  # row 3
    # Step 4: place coin in "D" for bottom, row4, row3, row2
    board_instance.add_pos_to_board("D", 2)  # filler
    board_instance.add_pos_to_board("D", 2)  # filler
    board_instance.add_pos_to_board("D", 2)  # filler
    board_instance.add_pos_to_board("D", 1)  # row 2

    # Now we have a diagonal:
    # row2 colD, row3 colC, row4 colB, row5 colA all are player1
    assert board_instance.winner_check() == 1, (
        "Player 1 should have a diagonal TL-BR win."
    )


def test_winner_check_diagonal_bottom_left_to_top_right(board_instance):
    """
    Test a diagonal win (bottom-left to top-right).
    For example: row2 colA -> row3 colB -> row4 colC -> row5 colD,
    but counting from the bottom up in the board array indexing might differ.
    """
    # Another diagonal configuration:
    # We'll place 4 coins for player2 in a diagonal going from bottom-left
    # upward to the right.

    # One approach is to place them in rows 2..5, columns 0..3 (A..D).
    # We'll place filler coins to ensure they land in ascending rows.

    # For clarity, let's do something simpler:
    # - Place 3 filler coins in col A so the next player2 coin lands on row 2.
    for _ in range(3):
        board_instance.add_pos_to_board("A", 1)  # filler
    board_instance.add_pos_to_board("A", 2)  # row2

    # - Place 2 filler coins in col B so the next player2 coin lands on row 3
    for _ in range(2):
        board_instance.add_pos_to_board("B", 1)  # filler
    board_instance.add_pos_to_board("B", 2)  # row3

    # - Place 1 filler coin in col C so the next player2 coin lands on row 4
    board_instance.add_pos_to_board("C", 1)  # filler
    board_instance.add_pos_to_board("C", 2)  # row4

    # - The next coin in col D lands on row 5
    board_instance.add_pos_to_board("D", 2)  # row5

    # Check
    assert board_instance.winner_check() == 2, (
        "Player 2 should have a diagonal BL-TR win."
    )
