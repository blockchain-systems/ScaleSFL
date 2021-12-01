import os
import re
import json
import base64
import requests
import threading
from flask import Flask
from flask import request, abort

from src.client import client_pipline
from src.utils.model import client_model_info, deserialize_model, model_info
from src.utils.endorsement import endorse_model

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


if __name__ == "__main__":
    # Start Flask
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()

    # Start flower
    client, start_client = client_pipline()
    start_client()
