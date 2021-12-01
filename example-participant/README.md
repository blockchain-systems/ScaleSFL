# Federated Learning with Flower

For the Example Participant, we use the [Flower](https://flower.dev/) framekwork. We follow the excellent tutorials from the [docs](https://flower.dev/docs/), to setup a federated learning server, and client. In our scenario, each participant will act as both a client and server.

This will run a gRPC server for federated learning, and we also make use of a local [Flask](https://flask.palletsprojects.com) server to handle our implementation specific needs (such as a way for the peer to evaluate models).

We also make use of the [Fabric SDK](https://github.com/hyperledger/fabric-sdk-py) here to submit models to the ledger.

# How to Run

First make sure you have the required version of python installed (^3.9), and install poetry

```sh
pip install poetry --user
```

Next we'll install the required dependencies for this project

```sh
poetry install
```

Since PyTorch is dependent on system, please install a version of [PyTorch](https://pytorch.org/get-started/locally/) (if no supported GPU, make sure to install CPU)

e.g. for Linux with CUDA 10.2:

```sh
pip3 install torch torchvision torchaudio
```

If a requirements.txt file is needed, you can generate it with:

```sh
pip list --not-required --format freeze > requirements.txt
```

Finally you can start the servers by running

```sh
./run.sh
```
