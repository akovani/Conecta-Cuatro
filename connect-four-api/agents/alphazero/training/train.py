from datetime import datetime
import time

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


from agents.alphazero.alphazero_model import AlphaZeroModel
from agents.alphazero.helpers import board_to_channels

from torch.utils.tensorboard import SummaryWriter


def train_on_data(
    model,
    data,
    writer,
    global_step_start,
    epochs=1,
    batch_size=64,
    lr=1e-3,
    device="cpu",
):
    """
    Trains the given model on the provided data (list of (state, policy, value)).
    Logs the loss in TensorBoard.

    Args:
        model: Policy-Value network.
        data: List of (np.array(6,7), np.array(7), scalar_value).
        writer: TensorBoard SummaryWriter object.
        global_step_start: Step counter before training starts (will be incremented).
        epochs: Number of epochs.
        batch_size: Size of the batches.
        lr: Learning rate.
        device: "cpu" or "cuda".

    Returns:
        global_step: Incremented value after training.
    """
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.to(device)
    model.train()

    if len(data) < batch_size:
        batch_size = max(1, len(data))  # Use smaller batch size if necessary
        print(f"Warning: Reduced batch size to {batch_size} due to limited data")

    # Shuffle data
    np.random.shuffle(data)

    global_step = global_step_start

    for epoch in range(epochs):
        start_time_epoch = time.time()
        batch_losses = []

        # Calculate number of full batches
        num_full_batches = len(data) // batch_size

        # Process full batches
        for i in range(num_full_batches):
            batch = data[i * batch_size : (i + 1) * batch_size]

            # Lists for States, Policies, Values
            states_list = []
            policies_list = []
            values_list = []

            for state, policy, value in batch:
                c3 = board_to_channels(state)
                states_list.append(c3)
                policies_list.append(policy)
                values_list.append(value)

            # Convert to NumPy arrays
            states_np = np.array(states_list, dtype=np.float32)
            policies_np = np.array(policies_list, dtype=np.float32)
            values_np = np.array(values_list, dtype=np.float32)

            # Convert to Torch tensors
            states_t = torch.from_numpy(states_np).to(device)
            policies_t = torch.from_numpy(policies_np).to(device)
            values_t = torch.from_numpy(values_np).to(device)

            # Forward pass
            policy_pred, value_pred = model(states_t)
            log_prob = torch.log_softmax(policy_pred, dim=1)
            policy_loss = -torch.mean(torch.sum(policies_t * log_prob, dim=1))

            value_pred = value_pred.view(-1)
            value_loss = nn.MSELoss()(value_pred, values_t)

            loss = policy_loss + value_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            batch_losses.append(loss.item())

            # Logging in TensorBoard per batch
            global_step += 1
            writer.add_scalar("Loss/Train", loss.item(), global_step)

        remaining_data = len(data) % batch_size
        if remaining_data > 0:
            print(f"  Skipping {remaining_data} samples to avoid batch size issues")

        avg_epoch_loss = np.mean(batch_losses)
        end_time_epoch = time.time()  # Record time after epoch ends
        epoch_time = end_time_epoch - start_time_epoch  # Calculate epoch time

        print(
            f"  Epoch {epoch + 1}/{epochs}, Loss: {avg_epoch_loss:.4f}, Time: {epoch_time:.2f} seconds"
        )
        writer.add_scalar("Epoch Time/Train", epoch_time, epoch + 1)

    return global_step


def alphazero_training_loop(
    num_iterations=10, selfplay_games=10, n_simulations=50, epochs=5, device="cpu"
):
    """
    Minimal training loop for AlphaZero-like cycle.

    Args:
        num_iterations: Number of iterations.
        selfplay_games: Number of self-play games.
        n_simulations: Number of simulations.
        epochs: Number of epochs.
        device: "cpu" or "cuda".
    """
    from selfplay import generate_selfplay_data  # Adjust to your code if necessary

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    writer = SummaryWriter(log_dir=f"./runs/alphazero_connect4_{timestamp}")

    model = AlphaZeroModel().to(device)

    # Step counter for TensorBoard
    global_step = 0

    for i in range(num_iterations):
        start_time_iteration = time.time()
        print(f"=== ITERATION {i + 1}/{num_iterations} ===")

        # 1) Generate self-play data
        data = generate_selfplay_data(
            model, n_games=selfplay_games, n_simulations=n_simulations, device=device
        )
        print(f"  -> Generated {len(data)} training examples via self-play")

        # 2) Training
        model.train()
        global_step = train_on_data(
            model,
            data,
            writer,
            global_step,
            epochs=epochs,
            batch_size=64,
            lr=1e-3,
            device=device,
        )
        end_time_iteration = time.time()
        iteration_time = end_time_iteration - start_time_iteration
        print(
            f"  Iteration {i + 1}/{num_iterations} completed, Time: {iteration_time:.2f} seconds"
        )
        writer.add_scalar("Iteration Time/Train", iteration_time, i + 1)

    torch.save(model.state_dict(), "alphazero_connect_four.pt")
    print("Training completed. Model saved as alphazero_connect_four.pt")

    writer.close()
