from typing import Dict, Optional, Tuple
import flwr as fl

from .strategies import CommitteeStrategy
from .models.utils import set_parameters, load_model
from .datasets import load_CIFAR10
from .models.simple_cnn import create_model
from .models.evaluation.train_cls import test


def get_eval_fn():
    """Return an evaluation function for server-side evaluation."""

    # Load model
    net = create_model()

    # Use the last 5k training examples as a validation set
    _, testloader = load_CIFAR10()

    # The `evaluate` function will be called after every round
    def evaluate(weights: fl.common.Weights) -> Optional[Tuple[float, float]]:
        set_parameters(net, weights)  # Update model with the latest parameters
        loss, accuracy = test(net, testloader)

        return loss, {"accuracy": accuracy}

    return evaluate


def server_pipline(config: Dict[str, int] = {}):
    """Create strategy, start Flower server."""

    parameters = load_model()

    # Define strategy
    strategy = CommitteeStrategy(
        fraction_fit=1,
        fraction_eval=1,
        min_fit_clients=2,
        min_eval_clients=2,
        min_available_clients=2,
        eval_fn=get_eval_fn(),
        initial_parameters=parameters,
    )

    # Start client
    return strategy, lambda: fl.server.start_server(
        server_address="localhost:8080",
        config={"num_rounds": 1, **config},
        strategy=strategy,
    )


if __name__ == "__main__":
    _, start_server = server_pipline()
    start_server()
