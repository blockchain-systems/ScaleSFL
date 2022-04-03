import os
import copy
import typing
import warnings
import threading
from logging import INFO, log

import flwr as fl
from flwr.common import weights_to_parameters, ParametersRes
from opacus import PrivacyEngine

from .models.simple_cnn import create_model
from .models.evaluation.train_cls import train, test
from .models.utils import (
    get_parameters,
    set_parameters,
    count_parameters,
    model_info,
    ModelCheckpointInfo,
)
from .datasets import cifar10_noniid, mnist_noniid
from .utils.constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_LOCAL_EPOCHS,
    PRIVACY_TARGET_DELTA,
)


warnings.filterwarnings("ignore", category=UserWarning)


# Flower client
class CifarClient(fl.client.NumPyClient):
    def __init__(
        self,
        model,
        trainloader,
        testloader,
        *args,
        post_model: typing.Callable[[], typing.Dict] = None,
        differential_privacy=True,
        lock_inference=True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.post_model = post_model
        self.checkpoint_info = ModelCheckpointInfo(
            parameter_count=count_parameters(model)
        )

        # Worker lock
        self.lock = threading.RLock() if lock_inference else None

        # Model
        self.model = model

        # Dataset loaders
        self.trainloader = trainloader
        self.testloader = testloader

        # Differential Privacy Engine
        self.privacy_engine = PrivacyEngine() if differential_privacy else None

    def get_parameters(self):
        return get_parameters(self.model)

    def set_parameters(self, parameters):
        set_parameters(self.model, parameters)

    def fit(self, parameters, config={}):
        if self.lock:
            self.lock.acquire()
        try:
            # Train model
            self.set_parameters(parameters)
            train(
                self.model,
                self.trainloader,
                epochs=DEFAULT_LOCAL_EPOCHS,
                privacy_engine=self.privacy_engine,
            )

            # Privacy metrics
            privacy_info = {}
            if self.privacy_engine:
                self.checkpoint_info.epsilon = self.privacy_engine.get_epsilon(
                    PRIVACY_TARGET_DELTA
                )
                privacy_info = {"epsilon": self.checkpoint_info.epsilon}

            # Update checkpoint
            local_update = self.get_parameters()
            local_update_proto = weights_to_parameters(local_update)
            local_parameters_res = ParametersRes(parameters=local_update_proto)
            local_model_info = model_info(local_parameters_res)
            self.checkpoint_info.model_hash = local_model_info["model_hash"]
            self.checkpoint_info.serialized_model = local_model_info["serialized_model"]

            # If we are posting the model to the blockchain, evaluate it
            if self.post_model:
                self.evaluate(local_update)
                checkpoint = copy.copy(self.checkpoint_info)
        finally:
            if self.lock:
                self.lock.release()

        # Post model to the blockchain
        if self.post_model:
            self.post_model(checkpoint)

        return (
            local_update,
            len(self.trainloader),
            {**privacy_info},
        )

    def evaluate(self, parameters, config={}):
        if self.lock:
            self.lock.acquire()
        try:
            self.set_parameters(parameters)
            loss, accuracy = test(self.model, self.testloader)
            self.checkpoint_info.last_acc = accuracy
            self.checkpoint_info.highest_acc = max(
                self.checkpoint_info.highest_acc, accuracy
            )
        finally:
            self.lock.release()

        log(INFO, f"accuracy: {accuracy}")
        return float(loss), len(self.testloader), {"accuracy": float(accuracy)}


def client_pipeline(
    client_id: int = 0, num_clients: int = 0, lock_inference: bool = True
):
    """Create model, load data, define Flower client, start Flower client."""

    # Load model
    # net = create_model(in_channels=3, dim_out=10, img_size=32)
    net = create_model(in_channels=1, dim_out=10, img_size=28)
    # net = create_model(layer_dims=[28 * 28 * 1, 10])

    # Load data (CIFAR-10)
    trainloader, testloader = mnist_noniid(
        client_id=client_id, num_clients=num_clients, batch_size=DEFAULT_BATCH_SIZE
    )

    # Start client
    client = CifarClient(
        model=net,
        trainloader=trainloader,
        testloader=testloader,
        differential_privacy=(
            os.environ.get("CLIENT_USE_DIFFERENTIAL_PRIVACY", "True") == "True"
        ),
        lock_inference=lock_inference,
    )

    return client


if __name__ == "__main__":
    client = client_pipeline()
    fl.client.start_numpy_client("localhost:8080", client=client)
