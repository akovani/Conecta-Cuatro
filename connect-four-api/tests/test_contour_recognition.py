# test_your_module.py
# import numpy as np


# Adjust to match the actual module where your functions are defined
# from hardware.contour_recognition import is_floating_move


###############################
# Test is_floating_move
###############################
def test_is_floating_move_bottom_row():
    # """
    # If the stone is in the bottom row, it should never be considered 'floating'.
    # """
    # # Example: 6 rows x 7 columns (typical Connect4), last row index = 5
    # # Create an empty grid
    # grid = np.zeros((6, 7), dtype=int)
    # row, col = 5, 3  # bottom row
    # assert is_floating_move(grid, row, col) is False, (
    #     "Stone in bottom row must not be floating."
    # )
    pass


def test_is_floating_move_with_empty_cell_below():
    # """
    # If there is an empty cell (0) immediately under the stone, it should be considered 'floating'.
    # """
    # grid = np.zeros((6, 7), dtype=int)
    # row, col = 4, 2
    # # The bottom row is 5, so row=4 is one above the bottom.
    # # Keep grid[5][2] = 0 (empty), so it 'floats'
    # assert is_floating_move(grid, row, col) is True, (
    #     "Stone above an empty cell should be floating."
    # )
    pass


def test_is_floating_move_solid_below():
    # """
    # If the cell below the stone is occupied (non-zero), it should not be 'floating'.
    # """
    # grid = np.zeros((6, 7), dtype=int)
    # row, col = 4, 2
    # # Occupy the cell below with '1'
    # grid[5][2] = 1
    # assert is_floating_move(grid, row, col) is False, (
    #     "Stone should not float if the cell below it is occupied."
    # )
    pass


###############################
# Test detect_board_change
###############################


def test_detect_board_change_fails_no_image(monkeypatch):
    """
    Simulate cv2.imread returning None, triggering a ValueError.
    """

    # def mock_imread(path):
    #     return None  # No image found

    # monkeypatch.setattr("cv2.imread", mock_imread)

    # prev_board = np.zeros((6, 7), dtype=int)
    # with pytest.raises(ValueError, match="Failed to decode image from bytes."):
    #     detect_board_change(prev_board)
    pass


def test_detect_board_change_fails_no_change(monkeypatch):
    # class MockVideoCapture:
    #     def __init__(self, *args):
    #         pass

    #     def read(self):
    #         img = cv2.imread(r"tests/static/images/empty_field.png")
    #         return True, img

    # monkeypatch.setattr("cv2.VideoCapture", MockVideoCapture)

    # prev_board = np.zeros((6, 7), dtype=int)
    # with pytest.raises(
    #     ValueError, match="Ungültiger Zug erkannt oder mehrere Änderungen festgestellt."
    # ):
    #     detect_board_change(prev_board)
    pass


def test_detect_board_change_fails_grid_covered(monkeypatch):
    pass
    # Implement this test case


def test_detect_board_change_correctly(monkeypatch):
    # class MockVideoCapture:
    #     def __init__(self, *args):
    #         pass

    #     def read(self):
    #         img = cv2.imread(r"tests/static/images/standard_field.png")
    #         return True, img

    # monkeypatch.setattr("cv2.VideoCapture", MockVideoCapture)

    # prev_board = np.zeros((6, 7), dtype=int)

    # assert detect_board_change(prev_board) == ("A6", False)
    pass
