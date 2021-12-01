import os
import re
import json
import signal
import base64
import requests
import threading
from flask import Flask
from flask import request, abort
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from src.client import client_pipline
from src.utils.model import client_model_info, deserialize_model, model_info
from src.utils.endorsement import endorse_model
from src.fabric.chaincode import invoke_chaincode, query_chaincode

PORT = os.environ.get("PORT") or 3000
app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/model")
def model():
    info = client_model_info(client)

    return {
        "model_hash": info["model_hash"],
        "serialized_model": info["serialized_model"],
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
                serialized_model = res["serialized_model"]
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


# actions
START_FL = "start-fl"


if __name__ == "__main__":
    # Start Flask
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT))
    flask_thread.setDaemon(True)
    flask_thread.start()

    # Start flower
    while action := inquirer.select(
        message="What's next?",
        choices=[
            Choice(START_FL, name="Start FL Round"),
            Choice(value=None, name="Exit"),
        ],
        default=START_FL,
    ).execute():
        if action == START_FL:
            client, start_client = client_pipline()
            start_client()
