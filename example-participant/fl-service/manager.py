import os
import time
import glob
import argparse
import threading
import subprocess
from typing import Any, List
from dataclasses import dataclass

import flwr as fl
from flwr.common import (
    parameters_to_weights,
    weights_to_parameters,
)
from flwr.server.strategy.aggregate import aggregate
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from src.server import server_pipeline
from src.client import client_pipeline
from src.fabric.chaincode import query_chaincode
from src.models.utils import load_model, save_model
from src.utils import shard_balancers

parser = argparse.ArgumentParser(description="Run Federated Learning")

# Sample info
parser.add_argument(
    "--participants",
    "-p",
    type=int,
    help="Number of participants to launch",
    default=2,
)
parser.add_argument(
    "--shards",
    "-s",
    type=int,
    help="Number of shards available",
    default=2,
)
parser.add_argument(
    "--skip-client-creation",
    action="store_false",
    help="Skips the creation of FL clients",
)

# Client info
parser.add_argument(
    "--port",
    type=int,
    help="Starting port to launch clients",
    default=3000,
)
parser.add_argument(
    "--server-port",
    type=int,
    help="Starting port to launch flower server",
    default=8080,
)
parser.add_argument(
    "--differential-privacy",
    "-dp",
    action="store_true",
    help="Use differential privacy on clients",
)
device_parser = parser.add_mutually_exclusive_group()
device_parser.add_argument(
    "--gpu",
    action="store_true",
    help="Use GPU if available",
)
device_parser.add_argument(
    "--num-threads",
    type=int,
    help="How many threads each client should use",
    default=2,
)

# Config
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Increases the verbosity of output. Enable for debug output",
)


@dataclass
class ClientInfo:
    shard_id: int
    client_id: int
    server_port: int = 8080
    app_server: str = "http://localhost"
    fabric_server: str = "http://localhost"
    app_process: Any = None
    fabric_process: Any = None

    _app_starting_port = 3000
    _fabric_starting_port = 5000

    @property
    def app_port(self):
        return self.shard_id + ClientInfo._app_starting_port

    @property
    def fabric_port(self):
        return self.shard_id + ClientInfo._fabric_starting_port

    @property
    def app_url(self):
        return f"{self.app_server}:{self.app_port}"

    @property
    def fabric_url(self):
        return f"{self.fabric_server}:{self.fabric_port}"


def create_fl_client(
    client_info: ClientInfo,
    num_clients: int = 0,
    use_gpu: bool = True,
    num_threads: bool = 0,
    use_dp: bool = True,
    verbose: bool = False,
):
    env_vars = os.environ.copy()
    env_vars["PORT"] = str(client_info.app_port)
    env_vars["SERVER_PORT"] = str(client_info.server_port)
    env_vars["CLIENT_USE_GPU"] = str(use_gpu)
    env_vars["CLIENT_NUM_THREADS"] = str(num_threads)
    env_vars["CLIENT_USE_DIFFERENTIAL_PRIVACY"] = str(use_dp)
    env_vars["FABRIC_CHANNEL"] = f"shard{client_info.shard_id}"
    env_vars["CHAINCODE_CONTRACT"] = f"models{client_info.shard_id}"
    env_vars["TEST_SIMULATE_CLIENT_ID"] = str(client_info.client_id)
    env_vars["TEST_SIMULATE_CLIENTS_COUNT"] = str(num_clients)

    verbosity = (
        {} if verbose else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    )
    app_client = subprocess.Popen(["python", "app.py"], env=env_vars, **verbosity)

    return app_client


def create_fabric_client(client_info: ClientInfo, verbose: bool = False):
    env_vars = os.environ.copy()
    env_vars["PORT"] = str(client_info.fabric_port)
    env_vars["SHARD_ID"] = str(client_info.shard_id)

    verbosity = (
        {} if verbose else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    )
    fabric_client = subprocess.Popen(
        ["npm", "run", "start"],
        env=env_vars,
        cwd=os.path.join(os.getcwd(), "../fabric-sdk"),
        **verbosity,
    )

    return fabric_client


def ensure_fabric_clients(verbose: bool = False):
    created_client = False
    for client in clients:
        if not client.fabric_process:
            fabric_ps = create_fabric_client(client, verbose=verbose)
            print(f"Creating Fabric Client {client.client_id}: {client.fabric_url}")

            client.fabric_process = fabric_ps

            created_client = True

    if created_client:
        time.sleep(5)


def start_round(num_clients: int = 0, server_port: int = 8080):
    # Bug with flower causes simulations to fail if grequests is imported
    # See: https://github.com/mher/flower/issues/819
    import grequests

    print(f"Starting FL round: {round}")
    strategy, config = server_pipeline(num_clients=num_clients)
    start_server = lambda server_adress: fl.server.start_server(
        server_address=f"localhost:{server_adress}",
        config=config,
        strategy=strategy,
    )

    fl_server_thread = threading.Thread(target=lambda: start_server(server_port))
    fl_server_thread.setDaemon(True)
    fl_server_thread.start()

    time.sleep(2)

    reqs = []
    for client in clients:
        reqs.append(
            grequests.get(f"{client.app_url}/round/start", params={"round": round})
        )

    ress = grequests.map(reqs)
    for idx, res in enumerate(ress):
        client_info = res.json()
        print(f"FL Client {idx}: acc {client_info['last_acc']}")

    fl_server_thread.join()


def simulate_fl(num_clients: int = 0, num_shards: int = 0, num_epochs: int = 1):
    print(f"Starting FL simulation")
    client_fn = lambda cid: client_pipeline(
        client_id=int(cid), num_clients=num_clients, lock_inference=False
    )

    for _ in range(num_epochs):
        for shard_id in range(num_shards):
            strategy, config = server_pipeline(
                {"num_rounds": 3},
                num_clients=num_clients,
                server_defence=True,
                save_model_path=f"model/shard/{shard_id}/latest-weights.pkl",
                load_model_path=f"model/latest-weights.pkl",
            )

            fl.simulation.start_simulation(
                client_fn=client_fn,
                num_clients=num_clients,
                client_resources={"num_cpus": 1},
                **config,
                strategy=strategy,
            )

        weights_results = [
            (
                parameters_to_weights(
                    load_model(f"model/shard/{shard_id}/latest-weights.pkl")
                ),
                1,
            )
            for shard_id in range(num_shards)
        ]
        parameters = weights_to_parameters(aggregate(weights_results))
        save_model(parameters, file="model/latest-weights.pkl")


# actions
START_FL = "start-fl"
SIMULATE_FL = "simulate-fl"
GET_MODELS = "get-models"
GET_SHARDS = "get-shards"
DELETE_MODEL_CHECKPOINT = "delete-model-checkpoint"
DELETE_FABRIC_WALLET = "delete-wallets"

# local
clients: List[ClientInfo] = []
round = 0


if __name__ == "__main__":
    args = parser.parse_args()
    os.environ["CLIENT_USE_GPU"] = str(args.gpu)
    os.environ["CLIENT_USE_DIFFERENTIAL_PRIVACY"] = str(args.differential_privacy)

    try:
        ClientInfo._app_starting_port = args.port
        ClientInfo._fabric_starting_port = args.port + 2000

        # Start Clients
        for idx in range(args.participants):
            # Obtain the shardId
            shard_id = shard_balancers.round_robin(idx, args.shards)
            client_info = ClientInfo(
                shard_id=shard_id, client_id=idx, server_port=args.server_port
            )
            if args.skip_client_creation:
                fl_ps = create_fl_client(
                    client_info=client_info,
                    num_clients=args.participants,
                    use_gpu=args.gpu,
                    num_threads=args.num_threads,
                    use_dp=args.differential_privacy,
                    verbose=args.verbose,
                )
                client_info.app_process = fl_ps
                print(
                    f"Creating FL Client {client_info.client_id}: {client_info.app_url}"
                )

            clients.append(client_info)

        # Start flower
        while action := inquirer.select(
            message="What's next?",
            choices=[
                Choice(START_FL, name="Start FL Round"),
                Choice(SIMULATE_FL, name="Simulate FL"),
                Choice(GET_SHARDS, name="Query All Shards (catalyst)"),
                *[
                    Choice(f"{GET_MODELS}{s}", name=f"Query All Models (shard{s})")
                    for s in range(args.shards)
                ],
                Choice(DELETE_MODEL_CHECKPOINT, name="Delete Model Checkpoints"),
                Choice(DELETE_FABRIC_WALLET, name="Delete SDK Wallet IDs"),
                Choice(value=None, name="Exit"),
            ],
            default=START_FL,
        ).execute():
            if action == START_FL:
                round += 1
                ensure_fabric_clients(verbose=args.verbose)
                start_round(num_clients=args.participants, server_port=args.server_port)
            if action == SIMULATE_FL:
                # ensure_fabric_clients(verbose=args.verbose)
                simulate_fl(num_clients=args.participants, num_shards=args.shards)
            elif action.startswith(GET_MODELS):
                ensure_fabric_clients(verbose=args.verbose)
                shard_id = int(action[len(GET_MODELS) :])
                print(
                    query_chaincode(
                        f"shard{shard_id}",
                        f"models{shard_id}",
                        "GetAllModels",
                        [],
                        port=next(
                            client for client in clients if client.shard_id == shard_id
                        ).fabric_port,
                    )
                )
            elif action == GET_SHARDS:
                ensure_fabric_clients(verbose=args.verbose)
                print(query_chaincode("mainline", "catalyst", "GetAllShards", []))
            elif action == DELETE_MODEL_CHECKPOINT:
                model_files = glob.glob("model/*.pkl", recursive=True)
                if not model_files:
                    print("No checkpoints to delete!")
                else:
                    for model_chkpt in model_files:
                        proceed = inquirer.confirm(
                            message=f"Delete file {model_chkpt}?", default=True
                        ).execute()
                        if proceed:
                            os.remove(model_chkpt)
            elif action == DELETE_FABRIC_WALLET:
                wallet_files = glob.glob("../fabric-sdk/wallet/**/*.id", recursive=True)
                if not wallet_files:
                    print("No wallet IDs to delete!")
                else:
                    for wallet_id in wallet_files:
                        proceed = inquirer.confirm(
                            message=f"Delete file {wallet_id}?", default=True
                        ).execute()
                        if proceed:
                            os.remove(wallet_id)

    except Exception as e:
        print(f"manager.py Error: {e.with_traceback()}")
    finally:
        for client in clients:
            if client.app_process:
                client.app_process.terminate()
            if client.fabric_process:
                client.fabric_process.terminate()
