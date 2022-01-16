from flwr.common import ParametersRes, serde
from flwr.proto.transport_pb2 import ClientMessage


def serialize_model_params_res(parameters_res: ParametersRes):
    parameters_res_proto = serde.parameters_res_to_proto(parameters_res)
    serialized_model = parameters_res_proto.SerializeToString(True)

    return serialized_model


def deserialize_model(serialized_model: bytes):
    parameters_res_proto = ClientMessage.ParametersRes.FromString(serialized_model)
    return serde.parameters_res_from_proto(parameters_res_proto)
