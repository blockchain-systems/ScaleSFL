# Federated Learning with PySyft

Using [PySyft v0.5.0](https://github.com/OpenMined/PySyft/tree/syft_0.5.0)

Followng the [model-centric FL examples](https://github.com/OpenMined/PySyft/tree/syft_0.5.0/packages/syft/examples/federated-learning/model-centric)

```sh
pip install poetry --user

poetry install
```

Fabric SDK: https://github.com/hyperledger/fabric-sdk-py
Install a version of [PyTorch](https://pytorch.org/get-started/locally/) (if no supported GPU, make sure to install CPU)

```sh
docker run -it --rm --network host python3.9.7 bash
```

```sh
ssh-keygen -t rsa -f example_rsa
```

```sh
pip list --not-required --format freeze > requirements.txt
```

```sh
docker run -e PORT=7000 --rm --network host openmined/grid-domain
```
