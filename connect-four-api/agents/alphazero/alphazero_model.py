import torch
import torch.nn as nn
import torch.nn.functional as F


class AlphaZeroModel(nn.Module):
    """
    A deeper CNN for Connect Four, expecting input shape (B, 3, 6, 7).
    Features:
      - 4 convolutional layers with batch normalization
      - 64 filters each
      - 1 fully-connected layer (256 units)
      - Policy head -> shape (B,7)
      - Value head -> shape (B,1) with tanh activation
    """

    def __init__(self):
        super(AlphaZeroModel, self).__init__()

        # Convolutional stack:
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)

        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)

        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(64)

        # After 4 conv layers, the feature map is still (6,7) in height/width, but has 64 channels.
        # Flatten -> 64 * 6 * 7 = 2688
        self.fc1 = nn.Linear(64 * 6 * 7, 256)
        self.bn_fc1 = nn.BatchNorm1d(256)

        # Policy head (7 possible columns)
        self.policy_head = nn.Linear(256, 7)

        # Value head (scalar in [-1,1])
        self.value_head = nn.Linear(256, 1)

    def forward(self, x):
        """
        x: Tensor, shape (B, 3, 6, 7)
        Returns:
          policy: shape (B, 7)
          value: shape (B, 1)
        """
        # Convolutional layers
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))

        # Flatten
        x = x.view(x.size(0), -1)  # (B, 64*6*7) => (B, 2688)

        # Fully-connected
        x = F.relu(self.bn_fc1(self.fc1(x)))

        # Heads
        policy = self.policy_head(x)  # shape (B, 7)
        value = torch.tanh(self.value_head(x))  # shape (B, 1) in [-1,1]

        return policy, value
