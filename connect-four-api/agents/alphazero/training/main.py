import sys

import torch

from train import alphazero_training_loop
from evaluate import evaluate_model


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python main.py train [num_iterations] [selfplay_games] [n_simulations] [epochs] [device]"
        )
        print("  python main.py evaluate [num_games] [device]")
        return

    mode = sys.argv[1]

    if mode == "train":
        num_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        selfplay_games = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        n_simulations = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        epochs = int(sys.argv[5]) if len(sys.argv) > 5 else 5
        device = sys.argv[6] if len(sys.argv) > 6 else "cpu"

        if device == "cuda" and not torch.cuda.is_available():
            print("CUDA is not available. Switching to CPU...")
            device = "cpu"
        else:
            print(f"using GPU: {torch.cuda.get_device_name(0)}")

        alphazero_training_loop(
            num_iterations=num_iterations,
            selfplay_games=selfplay_games,
            n_simulations=n_simulations,
            epochs=epochs,
            device=device,
        )
    elif mode == "evaluate":
        num_games = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        device = sys.argv[3] if len(sys.argv) > 3 else "cpu"

        if device == "cuda" and not torch.cuda.is_available():
            print("CUDA is not available. Switching to CPU...")
            device = "cpu"

        evaluate_model(
            num_games=num_games, model_path="alphazero_connect_four.pt", device=device
        )
    else:
        print(f"Unknown Mode: {mode}")


if __name__ == "__main__":
    main()
