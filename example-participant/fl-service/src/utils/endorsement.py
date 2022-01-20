from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import Parameters
from flwr.common.typing import EvaluateIns


def endorse_model(
    client: NumPyClientWrapper, parameters: Parameters, accuracy_threshold=5
) -> bool:
    eval_res = client.evaluate(EvaluateIns(parameters=parameters, config={}))
    suspicious_accuracy = eval_res.metrics["accuracy"] or eval_res.accuracy
    local_accuracy = client.numpy_client.checkpoint_info.highest_acc

    return suspicious_accuracy > local_accuracy - accuracy_threshold
