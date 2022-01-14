from typing import List, Tuple
from flwr.common import (
    EvaluateRes,
    FitRes,
    Parameters,
    parameters_to_weights,
    weights_to_parameters,
)
from flwr.server.strategy.aggregate import aggregate
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg

from ..models.utils import save_model, model_info
from ..fabric.chaincode import query_chaincode


class CommitteeStrategy(FedAvg):
    def __init__(
        self,
        *args,
        client_port: int = 5000,
        fabric_channel: str = "shard1",
        chaincode_contract: str = "models",
        chaincode_model_exists_fn: str = "ModelExists",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client_port = client_port
        self.fabric_channel = fabric_channel
        self.chaincode_contract = chaincode_contract
        self.chaincode_model_exists_fn = chaincode_model_exists_fn

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
        """Aggregate fit results using weighted average."""
        # Do not aggregate if there are failures and failures are not accepted
        if not self.accept_failures and failures:
            return None, {}
        # Convert results
        endorsed_results = list(
            filter(
                lambda result: query_chaincode(
                    self.fabric_channel,
                    self.chaincode_contract,
                    self.chaincode_model_exists_fn,
                    [f"model_{model_info(result[1])['model_hash']}"],
                    port=self.client_port,
                ),
                results,
            )
        )
        if not endorsed_results:
            return None, {}
        weights_results = [
            (parameters_to_weights(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in endorsed_results
        ]
        parameters = weights_to_parameters(aggregate(weights_results))

        # Save aggregated_weights
        if parameters:
            print(f"Saving round {rnd} parameters...")
            save_model(parameters)

        return parameters, {}

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
