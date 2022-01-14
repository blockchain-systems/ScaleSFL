import os
import time
import glob
import argparse
import threading
import subprocess

import grequests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from src.server import server_pipline
from src.fabric.chaincode import query_chaincode

parser = argparse.ArgumentParser(description="Run Federated Learning")
parser.add_argument(
    "--participants",
    "-p",
    type=int,
    help="Number of participants to launch",
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
    "--verbose",
    "-v",
    action="store_true",
    help="Increases the verbosity of output. Enable for debug output",
)


def create_fl_client(
    port: int,
    client_id: int = 0,
    num_clients: int = 0,
    use_gpu: bool = True,
    verbose: bool = False,
):
    env_vars = os.environ.copy()
    env_vars["PORT"] = str(port)
    env_vars["CLIENT_USE_GPU"] = str(use_gpu)
    env_vars["TEST_SIMULATE_CLIENT_ID"] = str(client_id)
    env_vars["TEST_SIMULATE_CLIENTS_COUNT"] = str(num_clients)

    verbosity = (
        {} if verbose else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    )
    app_client = subprocess.Popen(["python", "app.py"], env=env_vars, **verbosity)

    return app_client, f"http://localhost:{env_vars['PORT']}"


def create_fabric_client(port: int, verbose: bool = False):
    env_vars = os.environ.copy()
    env_vars["PORT"] = str(port)

    verbosity = (
        {} if verbose else {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    )
    fabric_client = subprocess.Popen(
        ["npm", "run", "start"],
        env=env_vars,
        cwd=os.path.join(os.getcwd(), "../fabric-sdk"),
        **verbosity,
    )

    return fabric_client, f"http://localhost:{env_vars['PORT']}"


def ensure_fabric_clients(port: int, verbose: bool = False):
    created_client = False
    for idx, client in enumerate(clients):
        if not client["fabric_client_url"]:
            fabric_ps, fabric_url = create_fabric_client(port + idx + 2000)
            print(f"Creating Fabric Client {idx}: {fabric_url}")

            client["fabric_client_url"] = fabric_url
            client["fabric_client_process"] = fabric_ps

            created_client = True

    if created_client:
        time.sleep(5)


def start_round():
    print(f"Starting FL round: {round}")
    _, start_server = server_pipline()

    fl_server_thread = threading.Thread(target=lambda: start_server())
    fl_server_thread.setDaemon(True)
    fl_server_thread.start()

    time.sleep(2)

    reqs = []
    for client in clients:
        reqs.append(
            grequests.get(
                f"{client['app_client_url']}/round/start", params={"round": round}
            )
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
clients = []
round = 0


if __name__ == "__main__":
    args = parser.parse_args()
    os.environ["CLIENT_USE_GPU"] = str(args.gpu)

    try:
        # Start Clients
        for idx in range(args.participants):
            fl_ps, fl_url = create_fl_client(
                port=args.port + idx,
                client_id=idx,
                num_clients=args.participants,
                use_gpu=args.gpu,
                verbose=args.verbose,
            )
            print(f"Creating FL Client {idx}: {fl_url}")

            clients.append(
                {
                    "app_client_url": fl_url,
                    "app_client_process": fl_ps,
                    "fabric_client_url": None,
                    "fabric_client_process": None,
                }
            )

        # Start flower
        while action := inquirer.select(
            message="What's next?",
            choices=[
                Choice(START_FL, name="Start FL Round"),
                Choice(GET_MODELS, name="Query All Models (shard1)"),
                Choice(GET_SHARDS, name="Query All Shards (catalyst)"),
                Choice(DELETE_MODEL_CHECKPOINT, name="Delete Model Checkpoints"),
                Choice(DELETE_FABRIC_WALLET, name="Delete SDK Wallet IDs"),
                Choice(value=None, name="Exit"),
            ],
            default=START_FL,
        ).execute():
            if action == START_FL:
                round += 1
                ensure_fabric_clients(args.port, verbose=args.verbose)
                start_round()
            elif action == GET_MODELS:
                ensure_fabric_clients(args.port, verbose=args.verbose)
                print(query_chaincode("shard1", "models", "GetAllModels", []))
            elif action == GET_SHARDS:
                ensure_fabric_clients(args.port, verbose=args.verbose)
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
        print(f"manager.py Error: {e}")
    finally:
        for client in clients:
            if client["app_client_process"]:
                client["app_client_process"].terminate()
            if client["fabric_client_process"]:
                client["fabric_client_process"].terminate()
