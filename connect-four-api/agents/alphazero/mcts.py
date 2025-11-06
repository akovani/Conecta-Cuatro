import math
import numpy as np
import torch

from agents.alphazero.helpers import board_to_channels


class MCTSNode:
    def __init__(self, state, current_player, policy=None):
        """
        Initialize a Monte Carlo Tree Search (MCTS) node.

        Args:
            state (np.array): 6x7 board.
            current_player (int): 1 or 2.
            policy (dict, optional): {action: prior_probability}.
        """
        self.state = state
        self.current_player = current_player
        self.policy = policy if policy is not None else {}

        self.N = {}  # Visit counts per action
        self.W = {}  # Cumulative values per action
        self.children = {}  # Action -> MCTSNode
        self.is_expanded = False
        self.terminal = False
        self.winner = None
        self.value = 0.0  # Default

    def get_Q(self, action):
        """
        Calculate Q(s,a) = W(s,a)/N(s,a).

        Args:
            action: The action to evaluate.

        Returns:
            float: The Q value for the action.
        """
        if self.N.get(action, 0) == 0:
            return 0
        return self.W[action] / self.N[action]

    def get_U(self, action, c_puct=1.0):
        """
        Calculate U(s,a) = c_puct * P(s,a) * sqrt(sum(N(s,b))) / (1 + N(s,a)).

        Args:
            action: The action to evaluate.
            c_puct (float): The exploration constant.

        Returns:
            float: The U value for the action.
        """
        sumN = sum(self.N.get(a, 0) for a in self.N)
        return (
            c_puct
            * self.policy.get(action, 0)
            * math.sqrt(sumN + 1e-8)
            / (1 + self.N.get(action, 0))
        )


class MCTS:
    def __init__(
        self,
        env,
        model,
        c_puct=1.0,
        n_simulations=100,
        device="cpu",
        dirichlet_alpha=0.03,
        dirichlet_epsilon=0.25,
        add_root_noise=True,
    ):
        """
        Initialize the Monte Carlo Tree Search (MCTS).

        Args:
            env: The environment.
            model: The neural network model.
            c_puct (float): The exploration constant.
            n_simulations (int): Number of simulations.
            device (str): "cpu" or "cuda".
            dirichlet_alpha (float): Alpha parameter for Dirichlet noise.
            dirichlet_epsilon (float): Epsilon parameter for Dirichlet noise.
            add_root_noise (bool): Whether to add noise to the root node.
        """
        self.env = env
        self.model = model
        self.model.eval()
        self.c_puct = c_puct
        self.n_simulations = n_simulations
        self.device = device

        # Dirichlet noise parameters
        self.dirichlet_alpha = dirichlet_alpha
        self.dirichlet_epsilon = dirichlet_epsilon
        self.add_root_noise = add_root_noise

        self.root = None

    def search(self, state, current_player):
        """
        Start point of MCTS: Builds the tree starting from the root node.
        Returns the visit counts for each action.

        Args:
            state (np.array): The current state of the board.
            current_player (int): The current player (1 or 2).

        Returns:
            dict: Visit counts for each action.
        """
        if self.root is None or not np.array_equal(self.root.state, state):
            self.root = MCTSNode(state, current_player)

        for _ in range(self.n_simulations):
            self.simulate(self.root)

        act_visits = {a: self.root.N.get(a, 0) for a in self.root.policy}
        return act_visits

    def simulate(self, node):
        """
        Simulate a single playthrough from the given node.

        Args:
            node (MCTSNode): The node to start the simulation from.

        Returns:
            float: The value of the node.
        """
        if not node.is_expanded:
            self.expand(node)
            return -node.value

        best_action, next_node = self.select_child(node)

        if next_node is None:
            return -node.value

        value = self.simulate(next_node)

        node.N[best_action] = node.N.get(best_action, 0) + 1
        node.W[best_action] = node.W.get(best_action, 0) + value

        return -value

    def expand(self, node):
        """
        Expand the given node by adding all valid children.

        Args:
            node (MCTSNode): The node to expand.
        """
        if not hasattr(self, "_temp_env"):
            self._temp_env = ConnectFourEnvCopy(np.zeros((6, 7), dtype=int), 1)

        self._temp_env.set_state(node.state, node.current_player)
        temp_env = self._temp_env

        # Terminal checks
        if temp_env.is_done():
            node.terminal = True
            node.winner = temp_env.winner
            if node.winner == 0:
                node.value = 0
            elif node.winner == node.current_player:
                node.value = 1
            else:
                node.value = -1
            node.is_expanded = True
            return

        valid_actions = temp_env.get_valid_actions()
        if not valid_actions:
            node.terminal = True
            node.value = 0
            node.is_expanded = True
            return

        # Forward pass for policy + value
        channels = board_to_channels(node.state)
        state_input = torch.FloatTensor(channels).unsqueeze(0).to(self.device)

        with torch.no_grad():
            self.model.eval()
            policy_logits, value_pred = self.model(state_input)
            policy_probs = torch.softmax(policy_logits, dim=1).cpu().numpy()[0]
            value_pred = value_pred.item()

        policy_dict = {}
        for a in valid_actions:
            policy_dict[a] = policy_probs[a]

        # --- DIRICHLET NOISE if root ---
        if node == self.root and self.add_root_noise:
            alpha_array = [self.dirichlet_alpha] * len(valid_actions)
            noise = np.random.dirichlet(alpha_array)  # shape = (#valid_actions,)

            for i, a in enumerate(valid_actions):
                # p'(a) = (1 - eps) * p(a) + eps * noise[i]
                policy_dict[a] = (1.0 - self.dirichlet_epsilon) * policy_dict[
                    a
                ] + self.dirichlet_epsilon * noise[i]

        # Normalize after possible noise
        sum_p = sum(policy_dict.values())
        if sum_p > 0:
            for a in policy_dict:
                policy_dict[a] /= sum_p
        else:
            for a in policy_dict:
                policy_dict[a] = 1.0 / len(policy_dict)

        # Save results
        node.policy = policy_dict
        node.value = value_pred
        node.is_expanded = True

        # Create children
        for a in valid_actions:
            next_state, next_player, done, winner = temp_env.step(a)
            child_node = MCTSNode(next_state, next_player)
            node.children[a] = child_node

    def select_child(self, node):
        """
        Select the best child node based on the UCT value.

        Args:
            node (MCTSNode): The node to select the child from.

        Returns:
            tuple: The best action and the corresponding child node.
        """
        best_value = -float("inf")
        best_action = None
        best_child = None

        for action, child in node.children.items():
            q_value = node.get_Q(action)
            u_value = node.get_U(action, self.c_puct)
            score = q_value + u_value
            if score > best_value:
                best_value = score
                best_action = action
                best_child = child

        # If there are no children or best_child was never set:
        if best_child is None:
            # We have no child nodes -> Terminal state or error case
            return None, None

        return best_action, best_child


class ConnectFourEnvCopy:
    """
    Helper class for MCTS: Executes a step on a copy of the board
    to check terminal states, etc.
    """

    def __init__(self, state, current_player):
        """
        Initialize the environment copy.

        Args:
            state (np.array): The initial state of the board.
            current_player (int): The current player (1 or 2).
        """
        self.state = state.copy()
        self.current_player = current_player
        self.rows, self.cols = self.state.shape
        self.done = False
        self.winner = None
        if self.check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player

    def set_state(self, state, current_player):
        """
        Set the state of the environment without creating a new object.

        Args:
            state (np.array): The state to set.
            current_player (int): The current player (1 or 2).
        """
        self.state = state.copy()
        self.current_player = current_player
        self.rows, self.cols = self.state.shape
        self.done = False
        self.winner = None
        if self.check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player

    def is_done(self):
        """
        Check if the game is done.

        Returns:
            bool: True if the game is done, False otherwise.
        """
        if self.done:
            return True
        if self.check_draw():
            self.done = True
            self.winner = 0
            return True
        return False

    def get_valid_actions(self):
        """
        Get the list of valid actions.

        Returns:
            list: List of valid actions.
        """
        valid_actions = []
        for c in range(self.cols):
            if self.state[0][c] == 0:  # If the top row in column c is empty
                valid_actions.append(c)
        return valid_actions

    def step(self, action):
        """
        Execute a step in the environment.

        Args:
            action (int): The action to execute.

        Returns:
            tuple: The new state, the next player, whether the game is done, and the winner.
        """
        if self.done:
            return self.state, self.current_player, True, self.winner

        # Invalid -> Terminal
        if self.state[0][action] != 0:
            self.done = True
            self.winner = 3
            return self.state, self.current_player, True, 3

        row = -1
        for r in range(self.rows - 1, -1, -1):
            if self.state[r][action] == 0:
                row = r
                break
        self.state[row][action] = self.current_player

        if self.check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player
        elif self.check_draw():
            self.done = True
            self.winner = 0

        next_player = 2 if self.current_player == 1 else 1
        return self.state.copy(), next_player, self.done, self.winner

    def check_winner(self, player):
        """
        Check if the given player has won.

        Args:
            player (int): The player to check.

        Returns:
            bool: True if the player has won, False otherwise.
        """
        board = self.state
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if (
                    board[r][c] == player
                    and board[r][c + 1] == player
                    and board[r][c + 2] == player
                    and board[r][c + 3] == player
                ):
                    return True
        # Vertical
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if (
                    board[r][c] == player
                    and board[r + 1][c] == player
                    and board[r + 2][c] == player
                    and board[r + 3][c] == player
                ):
                    return True
        # Diagonal
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if (
                    board[r][c] == player
                    and board[r + 1][c + 1] == player
                    and board[r + 2][c + 2] == player
                    and board[r + 3][c + 3] == player
                ):
                    return True
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                if (
                    board[r][c] == player
                    and board[r - 1][c + 1] == player
                    and board[r - 2][c + 2] == player
                    and board[r - 3][c + 3] == player
                ):
                    return True

        return False

    def check_draw(self):
        """
        Check if the game is a draw.

        Returns:
            bool: True if the game is a draw, False otherwise.
        """
        return np.all(self.state != 0)
