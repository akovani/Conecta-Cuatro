import pytest
import numpy as np

# Import the functions you want to test
# Adjust the import paths as necessary
from util import (
    board_state_to_env_board,
    env_board_to_board_state,
    get_algorithm_params,
)


################################################
# Tests for board_state_to_env_board
################################################
def test_board_state_to_env_board_basic():
    board_state = [[0, 1, 2], [2, 1, 0], [1, 0, 2]]
    env_board = board_state_to_env_board(board_state)

    # Check that output is a NumPy array
    assert isinstance(env_board, np.ndarray), "Output should be a numpy array."

    # Check if the shape matches
    assert env_board.shape == (3, 3), "Output shape should match input."

    # Check if contents match
    np.testing.assert_array_equal(env_board, np.array(board_state))


################################################
# Tests for env_board_to_board_state
################################################
def test_env_board_to_board_state_basic():
    env_board = np.array([[0, 1, 2], [2, 1, 0]])
    board_state = env_board_to_board_state(env_board)

    # Check that output is a list of lists
    assert isinstance(board_state, list), "Output should be a list."
    for row in board_state:
        assert isinstance(row, list), "Each row should be a list."

    # Check if the dimensions match
    assert len(board_state) == 2, "Outer list should have length 2."
    assert len(board_state[0]) == 3, "Inner list should have length 3."

    # Check if contents match
    assert board_state == env_board.tolist(), (
        "Contents should match the original array."
    )


################################################
# Tests for get_algorithm_params
################################################


def test_get_algorithm_params_minimax_easy(mocker):
    # Example constants you might mock; adjust as appropriate.
    # This demonstration assumes you mock them if needed.
    # If you rely on the real constants, remove or adapt this part.
    mocker.patch("util.MINIMAX_EASY_DEPTH", 1)
    mocker.patch("util.MINIMAX_MEDIUM_DEPTH", 2)
    mocker.patch("util.MINIMAX_HARD_DEPTH", 3)

    params = get_algorithm_params("MiniMax", 1)
    assert "minimax_depth" in params
    assert params["minimax_depth"] == 1


def test_get_algorithm_params_minimax_medium(mocker):
    mocker.patch("util.MINIMAX_EASY_DEPTH", 1)
    mocker.patch("util.MINIMAX_MEDIUM_DEPTH", 2)
    mocker.patch("util.MINIMAX_HARD_DEPTH", 3)

    params = get_algorithm_params("MiniMax", 2)
    assert "minimax_depth" in params
    assert params["minimax_depth"] == 2


def test_get_algorithm_params_mcts_easy(mocker):
    mocker.patch("util.MCTS_EASY_SIMULATIONS", 10)
    mocker.patch("util.MCTS_MEDIUM_SIMULATIONS", 20)
    mocker.patch("util.MCTS_HARD_SIMULATIONS", 30)
    mocker.patch("util.MCTS_EASY_EXPLORATION", 0.5)
    mocker.patch("util.MCTS_MEDIUM_EXPLORATION", 1.0)
    mocker.patch("util.MCTS_HARD_EXPLORATION", 1.5)

    params = get_algorithm_params("MCTS", 1)
    assert "mcts_sim" in params
    assert "expl_rate" in params
    assert params["mcts_sim"] == 10
    assert params["expl_rate"] == 0.5


def test_get_algorithm_params_ai_mode():
    # "AI_Mode" should return an empty dict
    params = get_algorithm_params("AI_Mode", 3)
    assert isinstance(params, dict)
    assert len(params) == 0, "Expected empty dict for AI_Mode."


def test_get_algorithm_params_invalid_difficulty():
    with pytest.raises(ValueError, match="Difficulty must be between 1 and 3"):
        get_algorithm_params("MiniMax", 0)  # Invalid difficulty


def test_get_algorithm_params_invalid_mode():
    with pytest.raises(ValueError, match="Invalid mode"):
        get_algorithm_params("InvalidMode", 1)  # Invalid mode
