import os
import time
import glob
import argparse
import threading
import subprocess
from typing import Any, List
from dataclasses import dataclass

import grequests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from src.server import server_pipline
from src.fabric.chaincode import query_chaincode
from src.utils import shard_balancers

parser = argparse.ArgumentParser(description="Run Federated Learning")
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
    "--port",
    type=int,
    help="Starting port to launch clients",
    default=3000,
)
parser.add_argument(
    "--gpu",
    action="store_true",
    help="Use GPU if available",
)
parser.add_argument(
    "--differential-privacy",
    "-dp",
    action="store_true",
    help="Use differential privacy on clients",
)
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
    use_dp: bool = True,
    verbose: bool = False,
):
    env_vars = os.environ.copy()
    env_vars["PORT"] = str(client_info.app_port)
    env_vars["CLIENT_USE_GPU"] = str(use_gpu)
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


def start_round(num_clients: int = 0):
    print(f"Starting FL round: {round}")
    _, start_server = server_pipline(num_clients=num_clients)

    fl_server_thread = threading.Thread(target=lambda: start_server())
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


# actions
START_FL = "start-fl"
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
            client_info = ClientInfo(shard_id=shard_id, client_id=idx)
            fl_ps = create_fl_client(
                client_info=client_info,
                num_clients=args.participants,
                use_gpu=args.gpu,
                use_dp=args.differential_privacy,
                verbose=args.verbose,
            )
            client_info.app_process = fl_ps
            print(f"Creating FL Client {client_info.client_id}: {client_info.app_url}")

            clients.append(client_info)

        # Start flower
        while action := inquirer.select(
            message="What's next?",
            choices=[
                Choice(START_FL, name="Start FL Round"),
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
                start_round(num_clients=args.participants)
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
