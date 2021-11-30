import os
import hashlib
import threading
from flask import Flask
from flask import request
from flwr.common import serde

from src.client import client_pipline

PORT = os.environ.get("PORT") or 3000
app = Flask(__name__)

lol = 0


@app.route("/")
def index():
    global lol
    lol += 1
    return "Hello World!" + str(lol)


@app.route("/model")
def model_info():
    parameters_res = client.get_parameters()
    parameters_res_proto = serde.parameters_res_to_proto(parameters_res)
    serialized_model = parameters_res_proto.SerializeToString(True)

    return {"model_hash": hashlib.sha256(serialized_model).hexdigest()}


@app.route("/evaluate", methods=["POST"])
def evaluate_model():
    serialized_model = request.data
    pass


if __name__ == "__main__":
    # Start Flask
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()

    # Start flower
    # client, start_client = client_pipline()
    # start_client()
