import os
import random

import torch
import numpy as np

from ...utils.constants import SEED


# Reproducibility
torch.manual_seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

# Torch device
def get_device(cpu=False):
    USE_GPU = os.environ.get("CLIENT_USE_GPU", "True") == "True"
    NUM_THREADS = int(os.environ.get("CLIENT_NUM_THREADS", 0))

    if USE_GPU and not cpu:
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    if NUM_THREADS:
        torch.set_num_threads(NUM_THREADS)
    return torch.device("cpu")
