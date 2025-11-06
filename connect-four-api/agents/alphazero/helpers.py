import numpy as np
# import torch


def col_to_letter(col_index):
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    return letters[col_index]


def letter_to_col(letter):
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    return letters.index(letter.upper())


# def board_to_channels(board):
#     board_tensor = torch.tensor(board, dtype=torch.int)
#     p1_map = (board_tensor == 1).float()
#     p2_map = (board_tensor == 2).float()
#     empty_map = (board_tensor == 0).float()
#     return torch.stack([p1_map, p2_map, empty_map], axis=0)


def board_to_channels(board):
    p1_map = (board == 1).astype(np.float32)
    p2_map = (board == 2).astype(np.float32)
    empty_map = (board == 0).astype(np.float32)
    return np.stack([p1_map, p2_map, empty_map], axis=0)  # shape (3,6,7)
