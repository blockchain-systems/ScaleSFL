import os
import re
import json
import base64
import warnings

import requests
from flask import Flask
from flask import request, abort

from src.client import client_pipline
from src.models.utils import client_model_info, deserialize_model, model_info
from src.utils.endorsement import endorse_model
from src.fabric.chaincode import invoke_chaincode

PORT = int(os.environ.get("PORT", 3000))
CLIENT_PORT = int(os.environ.get("CLIENT_PORT", PORT)) + 2000
FABRIC_CHANNEL = os.environ.get("FABRIC_CHANNEL", "shard1")
CHAINCODE_CONTRACT = os.environ.get("CHAINCODE_CONTRACT", "models")
CHAINCODE_CREATE_MODEL_FN = os.environ.get("CHAINCODE_CREATE_MODEL_FN", "CreateModel")

TEST_COMPARE_MODEL_HASH = os.environ.get("TEST_COMPARE_MODEL_HASH", True)
TEST_SIMULATE_CLIENT_ID = int(os.environ.get("TEST_SIMULATE_CLIENT_ID", 0))
TEST_SIMULATE_CLIENTS_COUNT = int(os.environ.get("TEST_SIMULATE_CLIENTS_COUNT", 0))
app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/round/start")
def start_fl():
    round = request.args.get("round")

    def post_model():
        client.numpy_client.evaluate(client.numpy_client.get_parameters())

        # push weights learned locally
        info = client_model_info(client)
        invoke_chaincode(
            FABRIC_CHANNEL,
            CHAINCODE_CONTRACT,
            CHAINCODE_CREATE_MODEL_FN,
            [
                f"model_{info['model_hash']}",
                info["model_hash"],
                PORT,
                request.host_url,
                round,
                client.numpy_client.checkpoint_info["last_acc"],
            ],
            port=CLIENT_PORT,
        )

        return info

    # Start a round of FL
    client.numpy_client.post_model = post_model
    start_client()

    return client.numpy_client.checkpoint_info


@app.route("/model")
def model():
    info = client_model_info(client)

    return {
        "model_hash": info["model_hash"],
        "serialized_model": info["serialized_model"],
        "last_acc": info["last_acc"],
        "highest_acc": info["highest_acc"],
    }


@app.route("/model/hash")
def model_info_hash():
    info = client_model_info(client)

    return {"model_hash": info["model_hash"]}


@app.route("/evaluate", methods=["POST"])
def evaluate_model():
    serialized_model = request.data
    parameters_res = deserialize_model(serialized_model)

    eval_res = client.evaluate({"parameters": parameters_res.parameters, "config": {}})
    eval = json.dumps(eval_res)

    return eval


@app.route("/endorse/evaluate", methods=["POST"])
def evaluate_rwset():
    rwSet = json.loads(request.data)
    nsRwSets = rwSet["NsRwSets"]
    for nsRwSet in nsRwSets:
        ns = nsRwSet["NameSpace"]
        kvRwSet = nsRwSet["KvRwSet"]
        # Check if the contract being called is a shard, and it is being written to
        if re.match("shard\d+", ns) and "writes" in kvRwSet:
            for write in kvRwSet["writes"]:
                _, bc_model = write["key"], json.loads(base64.decode(write["value"]))

                res = requests.get(f"{bc_model.Server}/model").json()
                serialized_model = bytes.fromhex(res["serialized_model"])
                model_hash = res["model_hash"]

                parameters_res = deserialize_model(serialized_model)
                parameters = parameters_res.parameters
                info = model_info(parameters_res)

                # check if the claimed hash matches the actual from parameters
                if TEST_COMPARE_MODEL_HASH and model_hash != info["model_hash"]:
                    abort(418)  # if not tell them they cant have coffee

                # check if model is good
                if not endorse_model(client, parameters):
                    abort(418)  # if not tell them they cant have coffee

    # return eval
    return {"status": 200}, 200


if __name__ == "__main__":
    if not TEST_COMPARE_MODEL_HASH:
        warnings.warn(
            f"Env varialbe 'TEST_COMPARE_MODEL_HASH', is set to {TEST_COMPARE_MODEL_HASH}, Only use this during testing"
        )

    # Start flower
    client, start_client = client_pipline(
        client_id=TEST_SIMULATE_CLIENT_ID, num_clients=TEST_SIMULATE_CLIENTS_COUNT
    )

    # Start Flask
    app.run(host="0.0.0.0", port=PORT)
