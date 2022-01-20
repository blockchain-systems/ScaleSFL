import hashlib
from dataclasses import dataclass
from collections import OrderedDict

import torch
import pandas as pd
from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import ParametersRes

from .serde import serialize_model_params_res


@dataclass
class ModelCheckpointInfo:
    model_hash: str = ""
    serialized_model: str = ""
    last_acc: int = 0
    highest_acc: int = 0
    parameter_count: int = 0
    epsilon: float = 0.0


def get_parameters(model):
    return [val.cpu().numpy() for _, val in model.state_dict().items()]


def set_parameters(model, parameters):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)


def count_parameters(model, breakdown=False, trainable=False):
    if breakdown:
        df_parameters = pd.DataFrame(
            [
                [name, p.numel()]
                for name, p in model.named_parameters()
                if not trainable or p.requires_grad
            ],
            columns=["module", "parameters"],
        )
        return df_parameters
    else:
        return sum(
            p.numel() for p in model.parameters() if not trainable or p.requires_grad
        )


def model_info(parameters_res: ParametersRes):
    serialized_model = serialize_model_params_res(parameters_res)

    return {
        "model_hash": hashlib.sha256(serialized_model).hexdigest(),
        "serialized_model": serialized_model.hex(),
    }


def client_model_info(client: NumPyClientWrapper):
    parameters_res = client.get_parameters()
    return {
        **model_info(parameters_res),
        "last_acc": client.numpy_client.checkpoint_info.last_acc,
        "highest_acc": client.numpy_client.checkpoint_info.highest_acc,
        "parameter_count": client.numpy_client.checkpoint_info.parameter_count,
        "epsilon": client.numpy_client.checkpoint_info.epsilon,
    }
