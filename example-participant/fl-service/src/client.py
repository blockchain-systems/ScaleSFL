import typing
import warnings
from logging import INFO, log
import flwr as fl
from flwr.client.numpy_client import NumPyClientWrapper
from requests.api import post

from .models.simple_cnn import create_model, train, test
from .utils.model import get_parameters, set_parameters
from .utils.dataset import load_CIFAR10


warnings.filterwarnings("ignore", category=UserWarning)


# TODO: add opacus to make clients DP
# TODO: client needs to be thread safe?
def client_pipline():
    """Create model, load data, define Flower client, start Flower client."""

    # Load model
    net = create_model()

    # Load data (CIFAR-10)
    trainloader, testloader = load_CIFAR10()

    # Flower client
    class CifarClient(fl.client.NumPyClient):
        def __init__(
            self,
            *args,
            post_model: typing.Callable[[], typing.Dict] = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.post_model = post_model
            self.checkpoint_info = {"highest_acc": 0, "last_acc": 0}

        def get_parameters(self):
            return get_parameters(net)

        def set_parameters(self, parameters):
            set_parameters(net, parameters)

        def fit(self, parameters, config={}):
            self.set_parameters(parameters)
            train(net, trainloader, epochs=1)
            if self.post_model is not None:
                model_info = self.post_model()
                if model_info is not None:
                    self.checkpoint_info = {**self.checkpoint_info, **model_info}
            return self.get_parameters(), len(trainloader), {}

        def evaluate(self, parameters, config={}):
            self.set_parameters(parameters)
            loss, accuracy = test(net, testloader)
            self.checkpoint_info["last_acc"] = accuracy
            self.checkpoint_info["highest_acc"] = max(
                self.checkpoint_info["highest_acc"], accuracy
            )
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
