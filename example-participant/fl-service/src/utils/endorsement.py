from flwr.client.numpy_client import NumPyClientWrapper
from flwr.common import Parameters
from flwr.common.typing import EvaluateIns


def endorse_model(client: NumPyClientWrapper, parameters: Parameters) -> bool:
    eval_res = client.evaluate(EvaluateIns(parameters=parameters, config={}))

    if (
        eval_res.metrics["accuracy"] or eval_res.accuracy
    ) < client.numpy_client.checkpoint_info["highest_acc"] - 5:
        return False

    return True
