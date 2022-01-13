import typing
import warnings
from logging import INFO, log
import flwr as fl
from flwr.client.numpy_client import NumPyClientWrapper
from opacus import PrivacyEngine

from .models.simple_cnn import create_model
from .models.evaluation.train_cls import train, test
from .models.utils import get_parameters, set_parameters
from .datasets import load_CIFAR10
from .utils.constants import DEFAULT_LOCAL_EPOCHS, PRIVACY_TARGET_DELTA


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
            model,
            trainloader,
            testloader,
            post_model: typing.Callable[[], typing.Dict] = None,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.post_model = post_model
            self.checkpoint_info = {"highest_acc": 0, "last_acc": 0}

            # Model
            self.model = model

            # Dataset loaders
            self.trainloader = trainloader
            self.testloader = testloader

            # Differential Privacy Engine
            self.privacy_engine = PrivacyEngine()

        def get_parameters(self):
            return get_parameters(self.model)

        def set_parameters(self, parameters):
            set_parameters(self.model, parameters)

        def fit(self, parameters, config={}):
            self.set_parameters(parameters)
            train(
                self.model,
                self.trainloader,
                epochs=DEFAULT_LOCAL_EPOCHS,
                privacy_engine=self.privacy_engine,
            )
            if self.post_model:
                model_info = self.post_model()
                if model_info:
                    self.checkpoint_info = {**self.checkpoint_info, **model_info}
            return (
                self.get_parameters(),
                len(self.trainloader),
                {"epsilon": self.privacy_engine.get_epsilon(PRIVACY_TARGET_DELTA)},
            )

        def evaluate(self, parameters, config={}):
            self.set_parameters(parameters)
            loss, accuracy = test(self.model, self.testloader)
            self.checkpoint_info["last_acc"] = accuracy
            self.checkpoint_info["highest_acc"] = max(
                self.checkpoint_info["highest_acc"], accuracy
            )
            log(INFO, f"accuracy: {accuracy}")
            return float(loss), len(self.testloader), {"accuracy": float(accuracy)}

    # Start client
    client = CifarClient(model=net, trainloader=trainloader, testloader=testloader)

    return NumPyClientWrapper(client), lambda: fl.client.start_numpy_client(
        "localhost:8080", client=client
    )


if __name__ == "__main__":
    _, start_client = client_pipline()
    start_client()
