import torch
from torch import nn
import torch.nn.functional as F

from .utils import get_device


class Net(nn.Module):
    def __init__(self, dim_in, dim_hidden, dim_out):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(dim_in, dim_hidden),
            nn.ReLU(),
            nn.Linear(dim_hidden, dim_out),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


def create_model(dim_in=32 * 32 * 3, dim_hidden=128, dim_out=10, device=get_device()):
    return Net(dim_in, dim_hidden, dim_out).to(device)
