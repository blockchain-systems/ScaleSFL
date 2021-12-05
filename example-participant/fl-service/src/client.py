from collections import OrderedDict
from logging import INFO, log
import warnings
import flwr as fl
from flwr.client.numpy_client import NumPyClientWrapper

from .models.simple_cnn import create_model, train, test
from .utils.model import get_parameters, set_parameters
from .utils.dataset import load_CIFAR10


warnings.filterwarnings("ignore", category=UserWarning)


# TODO: add opacus to make clients DP
def client_pipline():
    """Create model, load data, define Flower client, start Flower client."""

    # Load model
    net = create_model()

    # Load data (CIFAR-10)
    trainloader, testloader = load_CIFAR10()

    # Flower client
    class CifarClient(fl.client.NumPyClient):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.highest_acc = 0
            self.last_acc = 0

        def get_parameters(self):
            return get_parameters(net)

        def set_parameters(self, parameters):
            set_parameters(net, parameters)

        def fit(self, parameters, config):
            self.set_parameters(parameters)
            train(net, trainloader, epochs=1)
            return self.get_parameters(), len(trainloader), {}

        def evaluate(self, parameters, config={}):
            self.set_parameters(parameters)
            loss, accuracy = test(net, testloader)
            self.last_acc = accuracy
            self.highest_acc = max(self.highest_acc, accuracy)
            log(INFO, f"accuracy: {accuracy}")
            return float(loss), len(testloader), {"accuracy": float(accuracy)}

    # Start client
    client = CifarClient()

    return NumPyClientWrapper(client), lambda: fl.client.start_numpy_client(
        "localhost:8080", client=client
    )


if __name__ == "__main__":
    _, start_client = client_pipline()
    start_client()
