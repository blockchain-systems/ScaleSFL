from typing import Dict, Optional, Tuple
import flwr as fl

from .strategies import CommitteeStrategy
from .models.utils import set_parameters, load_model
from .datasets import mnist_test
from .models.mlp import create_model
from .models.evaluation.train_cls import test


def get_eval_fn():
    """Return an evaluation function for server-side evaluation."""

    # Load model
    # net = create_model(in_channels=1, dim_out=10, img_size=28)
    net = create_model(layer_dims=[28 * 28 * 1, 10])

    # Use the last 5k training examples as a validation set
    testloader = mnist_test()

    # The `evaluate` function will be called after every round
    def evaluate(weights: fl.common.Weights) -> Optional[Tuple[float, float]]:
        set_parameters(net, weights)  # Update model with the latest parameters
        loss, accuracy = test(net, testloader)

        return loss, {"accuracy": accuracy}

    return evaluate


def server_pipline(config: Dict[str, int] = {}, num_clients: int = 0):
    """Create strategy, start Flower server."""

    parameters = load_model()

    # Define strategy
    strategy = CommitteeStrategy(
        fraction_fit=1.0,
        fraction_eval=1.0,
        min_fit_clients=num_clients,
        min_eval_clients=num_clients,
        min_available_clients=num_clients,
        eval_fn=get_eval_fn(),
        initial_parameters=parameters,
        client_port=5000,
        fabric_channel="shard0",
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
