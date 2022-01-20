import os
import re
import json
import time
import base64
import warnings

import requests
from flask import Flask
from flask import request, abort
from flwr.common.typing import EvaluateIns

from src.client import client_pipline
from src.models.utils import (
    client_model_info,
    deserialize_model,
    model_info,
    ModelCheckpointInfo,
)
from src.utils.endorsement import endorse_model
from src.fabric.chaincode import invoke_chaincode

PORT = int(os.environ.get("PORT", 3000))
CLIENT_PORT = int(os.environ.get("CLIENT_PORT", PORT)) + 2000
FABRIC_CHANNEL = os.environ.get("FABRIC_CHANNEL", "shard0")
CHAINCODE_CONTRACT = os.environ.get("CHAINCODE_CONTRACT", "models0")
CHAINCODE_CREATE_MODEL_FN = os.environ.get("CHAINCODE_CREATE_MODEL_FN", "CreateModel")

TEST_SIMULATE_ENDORSE = os.environ.get("TEST_SIMULATE_ENDORSE", True) == True
TEST_SIMULATE_CLIENT_ID = int(os.environ.get("TEST_SIMULATE_CLIENT_ID", 0))
TEST_SIMULATE_CLIENTS_COUNT = int(os.environ.get("TEST_SIMULATE_CLIENTS_COUNT", 0))
app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/round/start")
def start_fl():
    round = request.args.get("round")

    def post_model(checkpoint_info: ModelCheckpointInfo):
        # push weights learned locally
        invoke_chaincode(
            FABRIC_CHANNEL,
            CHAINCODE_CONTRACT,
            CHAINCODE_CREATE_MODEL_FN,
            [
                f"model_{checkpoint_info.model_hash}",
                checkpoint_info.model_hash,
                PORT,
                request.host_url,
                round,
                checkpoint_info.last_acc,
            ],
            port=CLIENT_PORT,
        )

    # Start a round of FL
    client.numpy_client.post_model = post_model
    start_client()

    return client_model_info(client)


@app.route("/model")
def model():
    info = client_model_info(client)

    return {
        "model_hash": info["model_hash"],
        "serialized_model": info["serialized_model"],
        "last_acc": info["last_acc"],
        "highest_acc": info["highest_acc"],
        "parameter_count": info["parameter_count"],
        "epsilon": info["epsilon"],
    }


@app.route("/model/hash")
def model_info_hash():
    info = client_model_info(client)

    return {"model_hash": info["model_hash"]}


@app.route("/evaluate", methods=["POST"])
def evaluate_model():
    serialized_model = request.data
    parameters_res = deserialize_model(serialized_model)
    parameters = parameters_res.parameters

    eval_res = client.evaluate(EvaluateIns(parameters=parameters, config={}))
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
        if (
            re.match("models\d+", ns)
            and "writes" in kvRwSet
            and ns == CHAINCODE_CONTRACT
        ):
            for write in kvRwSet["writes"]:
                if TEST_SIMULATE_ENDORSE:
                    with client.numpy_client.lock:
                        time.sleep(1.4)
                    return {"status": 200}, 200

                _, bc_model = write["key"], json.loads(base64.b64decode(write["value"]))

                res = requests.get(f"{bc_model['Server']}/model").json()
                serialized_model = bytes.fromhex(res["serialized_model"])
                model_hash = res["model_hash"]

                parameters_res = deserialize_model(serialized_model)
                parameters = parameters_res.parameters
                info = model_info(parameters_res)

                # check if the claimed hash matches the actual from parameters
                if model_hash != info["model_hash"]:
                    abort(418)  # if not tell them they cant have coffee

                # check if model is good
                if not endorse_model(client, parameters):
                    abort(418)  # if not tell them they cant have coffee

    # return eval
    return {"status": 200}, 200


if __name__ == "__main__":
    if TEST_SIMULATE_ENDORSE:
        warnings.warn(
            f"Env varialbe 'TEST_SIMULATE_ENDORSE', is set to {TEST_SIMULATE_ENDORSE}, Only use this during testing"
        )

    # Start flower
    client, start_client = client_pipline(
        client_id=TEST_SIMULATE_CLIENT_ID, num_clients=TEST_SIMULATE_CLIENTS_COUNT
    )

    # Start Flask
    app.run(host="0.0.0.0", port=PORT, threaded=True, processes=1)
