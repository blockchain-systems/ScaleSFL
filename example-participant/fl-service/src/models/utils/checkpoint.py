import os
import pickle

from flwr.common import Parameters


def save_model(parameters: Parameters, file="model/latest-weights.pkl"):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "wb") as file:
        pickle.dump(parameters, file)


def load_model(file="model/latest-weights.pkl") -> Parameters:
    try:
        with open(file, "rb") as file:
            return pickle.load(file)
    except IOError:
        return None
