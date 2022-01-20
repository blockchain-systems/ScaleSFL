from typing import List

import torch
from torch import nn

from .utils import get_device


class Net(nn.Module):
    def __init__(self, layer_dims: List[int]):
        super().__init__()
        assert len(layer_dims) > 1

        # Define layers
        layers = []
        for dim_in, dim_out in zip(layer_dims[:-2], layer_dims[1:-1]):
            layers.append(nn.Linear(dim_in, dim_out), nn.ReLU())
        layers.append(nn.Linear(layer_dims[-2], layer_dims[-1]))

        # MLP
        self.fc = nn.Sequential(nn.Flatten(), *layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


def create_model(layer_dims: List[int] = [32 * 32 * 3, 10], device=None):
    if not device:
        device = get_device()

    return Net(layer_dims=layer_dims).to(device)
