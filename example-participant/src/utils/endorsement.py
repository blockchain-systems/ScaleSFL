from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import Parameters


def endorse_model(client: NumPyClientWrapper, parameters: Parameters) -> bool:
    eval_res = client.evaluate({"parameters": parameters, "config": {}})

    if (
        eval_res.metrics["accuracy"] or eval_res.accuracy
    ) < client.numpy_client.highest_acc - 5:
        return False

    return True
