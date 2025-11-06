# AlphaZero Connect Four – A (Nearly) Unbeatable Connect Four Bot

This project implements an AlphaZero-like AI for the game Connect Four. The goal is to train a strong game agent through self-play and Monte Carlo Tree Search (MCTS) in combination with a policy-value neural network. It uses a CNN architecture to evaluate the 6×7 board and can—after sufficient training—almost always win against human players and weaker opponents.


## 1. Project Overview
- Name: my_connect_four_alphazero (freely customizable)
- Main Goals:
    - Demonstrate an AlphaZero approach (similar to DeepMind's for Go/Chess) applied to the smaller game of Connect Four.
    - Enable training of a CNN-based policy-value AI through self-play.
    - Provide the option to play against the AI (via PyGame) or let the AI compete against other agents (e.g., random moves).


## 2. Structure and Functionality

### 2.1 Core Components

- `connect_four_environment.py`
    - Game logic (6×7 board, moves, win/draw detection).
- `alphazero_model.py`
    - Contains the neural network (CNN) with two output heads (Policy & Value).
- `mcts.py`
    - Implements Monte Carlo Tree Search, using the network to guide the search.
- `selfplay.py`
    - Conducts self-play matches: MCTS-based play against itself.
- `train.py`
    - Contains training logic: reads self-play data, calculates loss (Policy + Value), and optimizes over epochs.
- `evaluate.py` (optional)
    - Allows testing of the trained model against a random agent or another simple reference strategy.
- `test_game.py` (optional)
    - A PyGame frontend to personally play against the AI (AlphaZero-Connect-Four).

### 2.2 AI Approach

AlphaZero principle:
1. Self-play using MCTS.  
2. Store moves (Board, MCTS-Policy, Result).  
3. Train the policy-value network (neural network) on this data.  
4. Repeat (iterations) until the AI becomes very strong.

## 3. Installation
#### Requirements:

- Python 3.8+ (recommended).  
- PyTorch in a GPU-compatible version (e.g., cu118) if you want GPU training.
- Additional libraries: `numpy`, `pygame` (optional), etc.

#### Step-by-Step
1. Clone the repository or copy the files

```bash
git clone
cd my_connect_four_alphazero
``` 

2. Create a virtual environment

```bash
python -m venv .venv

# Linux/MacOS
source .venv/bin/activate  

# or Windows:
.venv\Scripts\activate
``` 

3. Install dependencies

```bash
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install numpy pygame
```
(Adjust the PyTorch version to your system, such as cu121 or the CPU version if no GPU is available.)

4. Verify structure

Your folders/files should look something like this:

```cpp
my_connect_four_alphazero/
├── main.py
├── connect_four_environment.py
├── alphazero_model.py
├── mcts.py
├── selfplay.py
├── train.py
├── evaluate.py
├── test_game.py
└── utils/
    ├── replay_buffer.py
    └── helpers.py
```

## 4. Usage
### 4.1. Start Training
Run the following command in your project directory:

```bash
python main.py train 30 50 100 5 cuda
```
Argument 1: Number of iterations (e.g., 30).  
Argument 2: Self-play games per iteration (e.g., 50).  
Argument 3: MCTS simulations per move (e.g., 100).  
Argument 4: Epochs per iteration (e.g., 5).  
Argument 5: `cuda` (or `cpu`), depending on whether you use a GPU.  

At the end, you will obtain a file `alphazero_connect_four.pt`, storing the trained model. You can also monitor the loss development in the console.

### 4.2. Evaluation
Against a random opponent (example):
```bash
python main.py evaluate 1000 cuda
```
Runs 1000 matches and logs the win rate.

Manual testing against AI (Pygame):
```bash
python test_game.py
```
Opens a PyGame window. Red (Player 1/AI) plays against Yellow (Player 2, Human).

### 4.3 Visualizing Training Progress with TensorBoard
1. Install TensorBoard: 
```bash
pip install tensorboard
```
2. Enable TensorBoard logging in the code:
    - In `train.py`, use a `SummaryWriter`.
    - Log loss per batch/epoch:
        ```python
            from torch.utils.tensorboard import SummaryWriter

            writer = SummaryWriter(log_dir="./runs/alphazero_c4")
            ...
            # After each batch
            writer.add_scalar("Loss/Train", loss.item(), global_step)
            ...
            writer.close()  # after training
        ```
3. Start TensorBoard:
```bash
tensorboard --logdir=runs
```
Then open http://localhost:6006 in your browser. You will see interactive charts (loss curves, etc.).
Use this to detect overfitting or monitor learning progress, allowing you to fine-tune hyperparameters (e.g., learning rate) or network architecture.

## 5. Detailed Explanation of Training Process
The core of the project is an AlphaZero-like approach where MCTS and the policy-value network mutually reinforce each other. Training consists of multiple iterations, each with two main phases:

### 5.1. Self-Play (Generating Training Data)
#### 1. Initialization

The current neural network (`AlphaZeroCNN`) is used for decision-making.
The game starts on an empty 6×7 board.

#### 2. MCTS

For each move, the program performs Monte Carlo Tree Search:
- Expands possible moves
- Evaluates with the network (Policy + Value)
- Selects the action with the highest statistical Q+U value

After MCTS simulations, we obtain a probability distribution over columns (0–6) based on visit counts of child nodes.

#### 3. Move Selection

For self-play, a column is chosen proportionally to these MCTS visit counts (optionally modified by a temperature > 0).
This introduces exploration (varied strategies) while maintaining focus on promising moves.

#### 4. Storing Results

For each board state, a tuple (state, MCTS-Policy, final result) is recorded.
Once the game ends (win/loss/draw), the final result ∈ {+1,−1,0} is known for each player.

#### 5. Repetition

Play, for example, 50 games per iteration, each generating multiple data pairs. Over time, hundreds to thousands of (Board, Policy, Value) datasets accumulate.

### 5.2. Training the Network (Policy + Value)
#### 1. Data Collection

The stored self-play pairs are loaded in batches.

#### 2. CNN Input

Each 6×7 board is converted into a (3,6,7) array (channels = Player1, Player2, empty cells).
It is passed to the neural network in tensor format (B,3,6,7).

#### 3. Prediction

The network outputs two values:
Policy: (B,7) – a probability distribution over the 7 columns.
Value: (B,1) – an estimate in [−1,+1] of how favorable the position is.

#### 4. Loss Calculation

Policy loss (e.g., cross-entropy) compares network policy πθ with MCTS policy πMCTS.
Value loss (e.g., MSELoss) compares network estimate 𝑣𝜃 with the actual final result.

#### 5. Optimization

Weights are adjusted via backpropagation, e.g., using the Adam optimizer.

## 6. References
Silver, D. et al. (2017). Mastering the game of Go without human knowledge. Nature, 550(7676), 354–359.
Silver, D. et al. (2018). A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play. Science, 362(6419), 1140–1144.
The approach follows these works but is significantly simplified for Connect Four.

## 7. Future Work
- **Hyperparameters:** Increasing the number of self-play games, MCTS simulations, etc., can improve results but at the cost of longer training time.
- **Minimax Testing:** Comparing the model against a classical alpha-beta search can provide an objective measure of its strength.
- **CNN Architecture Improvements:** Adding residual blocks, more layers, or batch normalization can further enhance the AI's performance.
