import numpy as np
from typing import List, Tuple
from flwr.common import EvaluateRes, FitRes, Parameters
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg

from ..utils.model import save_model


class CommitteeStrategy(FedAvg):
    def configure_fit(
        self, rnd: int, parameters: Parameters, client_manager: ClientManager
    ):
        return super().configure_fit(rnd, parameters, client_manager)

    def aggregate_fit(
        self,
        rnd: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException],
    ):
        parameters, config = super().aggregate_fit(rnd, results, failures)
        if parameters is not None:
            # Save aggregated_weights
            print(f"Saving round {rnd} parameters...")
            save_model(parameters)

        return parameters, config

    def configure_evaluate(
        self, rnd: int, parameters: Parameters, client_manager: ClientManager
    ):
        return super().configure_evaluate(rnd, parameters, client_manager)

    def aggregate_evaluate(
        self,
        rnd: int,
        results: List[Tuple[ClientProxy, EvaluateRes]],
        failures: List[BaseException],
    ):
        return super().aggregate_evaluate(rnd, results, failures)

    def evaluate(self, parameters: Parameters):
        return super().evaluate(parameters)
