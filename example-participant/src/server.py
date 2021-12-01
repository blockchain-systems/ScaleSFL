from typing import Optional, Tuple
import flwr as fl

from .strategies.committee_strategy import CommitteeStrategy
from .utils.model import set_parameters
from .utils.dataset import load_CIFAR10
from .models.simple_cnn import create_model, test


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


if __name__ == "__main__":
    # Define strategy
    strategy = CommitteeStrategy(
        fraction_fit=1,
        fraction_eval=1,
        min_fit_clients=1,
        min_eval_clients=2,
        min_available_clients=2,
        eval_fn=get_eval_fn(),
    )

    # Start server
    fl.server.start_server(
        server_address="localhost:8080",
        config={"num_rounds": 3},
        strategy=strategy,
    )
