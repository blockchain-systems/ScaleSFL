import hashlib
from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import serde


def model_info(client: NumPyClientWrapper):
    parameters_res = client.get_parameters()
    parameters_res_proto = serde.parameters_res_to_proto(parameters_res)
    serialized_model = parameters_res_proto.SerializeToString(True)

    return {
        "model_hash": hashlib.sha256(serialized_model).hexdigest(),
        "serialized_model": serialized_model,
    }


def deserialize_model(serialized_model: bytes):
    return serde.parameters_res_from_proto(serialized_model)
