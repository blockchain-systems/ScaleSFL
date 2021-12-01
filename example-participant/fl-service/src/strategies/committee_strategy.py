from typing import List, Tuple
import flwr as fl
from flwr.common import EvaluateRes, FitRes, Parameters
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg


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
        return super().aggregate_fit(rnd, results, failures)

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
