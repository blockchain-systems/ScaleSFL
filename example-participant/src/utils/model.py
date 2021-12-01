import torch
import hashlib
from collections import OrderedDict
from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import serde
from flwr.common import ParametersRes


def get_parameters(model):
    return [val.cpu().numpy() for _, val in model.state_dict().items()]


def set_parameters(model, parameters):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.Tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)


def serialize_model_params_res(parameters_res: ParametersRes):
    parameters_res_proto = serde.parameters_res_to_proto(parameters_res)
    serialized_model = parameters_res_proto.SerializeToString(True)

    return serialized_model


def deserialize_model(serialized_model: bytes):
    return serde.parameters_res_from_proto(serialized_model)


def model_info(parameters_res: ParametersRes):
    serialized_model = serialize_model_params_res(parameters_res)

    return {
        "model_hash": hashlib.sha256(serialized_model).hexdigest(),
        "serialized_model": serialized_model,
    }


def client_model_info(client: NumPyClientWrapper):
    parameters_res = client.get_parameters()
    return model_info(parameters_res)
