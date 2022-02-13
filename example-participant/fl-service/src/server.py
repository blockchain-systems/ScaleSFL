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


def server_pipeline(
    config: Dict[str, int] = {},
    num_clients: int = 0,
    server_defence: bool = False,
    save_model_path: str = "model/latest-weights.pkl",
    load_model_path: str = "model/latest-weights.pkl",
):
    """Create strategy, start Flower server."""

    parameters = load_model(file=load_model_path)

    # Define strategy
    strategy = CommitteeStrategy(
        fraction_fit=1.0,
        fraction_eval=1.0,
        min_fit_clients=num_clients,
        min_eval_clients=num_clients,
        min_available_clients=num_clients,
        eval_fn=get_eval_fn(),
        initial_parameters=parameters,
        server_defence=server_defence,
        save_model_path=save_model_path,
        client_port=5000,
        fabric_channel="shard0",
    )

    # Start client
    return strategy, {"num_rounds": 1, **config}


if __name__ == "__main__":
    strategy, config = server_pipeline()
    fl.server.start_server(
        server_address="localhost:8080",
        config=config,
        strategy=strategy,
    )
