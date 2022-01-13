import random

import torch
import numpy as np

from ...utils.constants import DEFAULT_USE_GPU, SEED


# Reproducibility
torch.manual_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

# Torch device
def get_device(cpu=False):
    if DEFAULT_USE_GPU and not cpu:
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    return torch.device("cpu")
