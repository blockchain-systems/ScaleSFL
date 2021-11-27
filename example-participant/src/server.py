import flwr as fl

from .strategies.committee_strategy import CommitteeStrategy

if __name__ == "__main__":
    # Define strategy
    strategy = CommitteeStrategy(
        fraction_fit=1,
        fraction_eval=1,
        min_fit_clients=1,
        min_eval_clients=2,
        min_available_clients=1,
    )

    # Start server
    fl.server.start_server(
        server_address="localhost:8080",
        config={"num_rounds": 3},
        strategy=strategy,
    )
