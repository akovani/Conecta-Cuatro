import torch
import numpy as np

from agents.alphazero.connect_four_environment import ConnectFourEnvironment
from agents.alphazero.alphazero_model import AlphaZeroModel
from agents.alphazero.mcts import MCTS


def load_alphazero_model(model_path="alphazero_connect_four.pt", device="cpu"):
    model = AlphaZeroModel().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model


def evaluate_model(num_games=50, model_path="alphazero_connect_four.pt", device="cpu"):
    """
    Lets the trained model (using MCTS) play against random opponents.
    :param num_games: Amount of games to play.
    :param model_path: Path to the model file.
    :param device: Device to use for evaluation.
    """
    model = load_alphazero_model(model_path, device)
    wins = 0
    draws = 0
    losses = 0

    for _ in range(num_games):
        env = ConnectFourEnvironment()
        done = False
        current_player = 1
        while not done:
            if current_player == 1:
                mcts = MCTS(env, model, c_puct=1.0, n_simulations=25, device=device)
                state = env.get_state()
                action_visits = mcts.search(state, current_player)
                best_action = max(action_visits, key=action_visits.get)
                next_state, reward, done = env.step(best_action)
            else:
                valid_actions = env.get_valid_actions()
                action = np.random.choice(valid_actions)
                next_state, reward, done = env.step(action)

            current_player = 2 if current_player == 1 else 1

            if done:
                if env.winner == 1:
                    wins += 1
                elif env.winner == 2:
                    losses += 1
                else:
                    draws += 1

    print(f"Results after {num_games} Games against random player:")
    print(f" - Wins  (AI)  : {wins}")
    print(f" - Draws: {draws}")
    print(f" - Losses   : {losses}")
