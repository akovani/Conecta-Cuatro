import numpy as np
# import torch

from agents.alphazero.connect_four_environment import ConnectFourEnvironment
from agents.alphazero.mcts import MCTS


def play_one_game(env, mcts, model, temperature=1.0):
    """
    Executes exactly one game in self-play mode.
    Returns a list of (state, mcts_prob, current_player) and the final result (Value).

    Args:
        env: The game environment.
        mcts: The Monte Carlo Tree Search object.
        model: The neural network model.
        temperature (float): The temperature parameter for exploration.

    Returns:
        list: A list of (state, mcts_prob, current_player) and the final result (Value).
    """
    states = []
    mcts_policies = []
    players = []

    done = False

    while not done:
        state = env.get_state()  # shape (6,7) int
        current_player = env.current_player

        action_visits = mcts.search(state, current_player)

        # visits => policy
        visit_sum = sum(action_visits[a] for a in action_visits)
        mcts_policy = np.zeros(7, dtype=float)
        for a in action_visits:
            mcts_policy[a] = action_visits[a]

        if visit_sum > 0:
            mcts_policy = mcts_policy / visit_sum

        # temperature
        if temperature > 0.0001:
            mcts_policy = mcts_policy ** (1.0 / temperature)
            mcts_policy = mcts_policy / np.sum(mcts_policy)

        # choose action stochastically
        action = np.random.choice(range(7), p=mcts_policy)

        states.append(state.copy())
        mcts_policies.append(mcts_policy)
        players.append(current_player)

        next_state, reward, done = env.step(action)

    winner = env.winner

    results = []
    for i in range(len(states)):
        if winner == 0:
            value = 0
        elif players[i] == winner:
            value = 1
        else:
            value = -1
        results.append((states[i], mcts_policies[i], value, players[i]))

    return results


def generate_selfplay_data(model, n_games=10, n_simulations=50, device="cpu"):
    """
    Generates training data using self-play (MCTS).
    Returns a list of (state, policy, value).

    Args:
        model: The neural network model.
        n_games (int): Number of self-play games to generate.
        n_simulations (int): Number of MCTS simulations per move.
        device (str): "cpu" or "cuda".

    Returns:
        list: A list of (state, policy, value).
    """
    data = []
    for _ in range(n_games):
        env = ConnectFourEnvironment()
        mcts = MCTS(
            env,
            model,
            c_puct=1.0,
            n_simulations=n_simulations,
            device=device,
            dirichlet_alpha=0.03,
            dirichlet_epsilon=0.25,
            add_root_noise=True,
        )
        game_data = play_one_game(env, mcts, model)
        for g in game_data:
            board, policy, val = g[0], g[1], g[2]
            data.append((board, policy, val))
    return data
