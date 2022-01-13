from math import floor

import torch
import numpy as np
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, Subset, random_split
from torchvision.datasets import CIFAR10, MNIST

from ..utils.constants import (
    CIFAR10_SHARDS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_TRAIN_SPLIT,
    MNIST_SHARDS,
    SEED,
)


transform_cifar10 = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
)
transform_mnist = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
)


def dataset_iid(
    dataset: Dataset,
    client_id: int = 0,
    num_clients: int = 0,
    batch_size: int = DEFAULT_BATCH_SIZE,
):
    """Load IID Dataset (training and test set)."""
    num_clients = max(num_clients, 1)

    # Partition data
    partitions = tuple([len(dataset) // num_clients] * num_clients)
    partitioned_data = random_split(
        dataset, partitions, generator=torch.Generator().manual_seed(SEED)
    )
    client_data = partitioned_data[client_id]
    split = floor(DEFAULT_TRAIN_SPLIT * len(client_data))

    # Client Train & Test set
    client_trainset = Subset(client_data, list(range(0, split)))
    client_testset = Subset(client_data, list(range(split, len(client_data))))

    # Dataloaders
    trainloader = DataLoader(client_trainset, batch_size=batch_size, shuffle=True)
    testloader = DataLoader(client_testset, batch_size=batch_size, shuffle=True)

    return trainloader, testloader


def dataset_noniid(
    dataset: Dataset,
    num_shards: int,
    client_id: int = 0,
    num_clients: int = 0,
    batch_size: int = DEFAULT_BATCH_SIZE,
):
    """Load non-IID Dataset (training and test set)."""
    num_imgs = len(dataset) // num_shards
    num_clients = max(num_clients, 1)
    shards_per = num_shards // num_clients
    np.random.seed(SEED)
    # Partition data
    shard_idxs = np.arange(num_shards)
    sample_idxs = np.arange(num_imgs * num_shards)
    sample_labels = np.array(dataset.targets)

    # Sort
    sample_pairs = np.vstack((sample_idxs, sample_labels))
    sample_pairs = sample_pairs[:, sample_pairs[1, :].argsort()]
    sample_idxs = sample_pairs[0, :]

    # Divide and assign
    np.random.shuffle(shard_idxs)
    client_shards = shard_idxs[client_id * shards_per : (client_id + 1) * shards_per]
    client_samples = np.concatenate(
        tuple(
            sample_idxs[x * num_imgs : x * num_imgs + num_imgs]
            for x in np.nditer(client_shards)
        )
    )

    # Get Client dataset and splits
    client_data = Subset(dataset, client_samples)
    split = floor(DEFAULT_TRAIN_SPLIT * len(client_data))
    train_idxs = np.arange(len(client_data))
    np.random.shuffle(train_idxs)

    # Client Train & Test set
    client_trainset = Subset(client_data, train_idxs[:split])
    client_testset = Subset(client_data, train_idxs[split:])

    # Dataloaders
    trainloader = DataLoader(client_trainset, batch_size=batch_size, shuffle=True)
    testloader = DataLoader(client_testset, batch_size=batch_size, shuffle=True)

    return trainloader, testloader


def cifar10_iid(
    client_id: int = 0, num_clients: int = 0, batch_size: int = DEFAULT_BATCH_SIZE
):
    """Load IID CIFAR-10 (training and test set)."""
    trainset = CIFAR10(
        "./dataset", train=True, download=True, transform=transform_cifar10
    )
    return dataset_iid(
        trainset, client_id=client_id, num_clients=num_clients, batch_size=batch_size
    )


def cifar10_noniid(
    client_id: int = 0, num_clients: int = 0, batch_size: int = DEFAULT_BATCH_SIZE
):
    """Load non-IID CIFAR-10 (training and test set)."""
    trainset = CIFAR10(
        "./dataset", train=True, download=True, transform=transform_cifar10
    )
    return dataset_noniid(
        trainset,
        CIFAR10_SHARDS,
        client_id=client_id,
        num_clients=num_clients,
        batch_size=batch_size,
    )


def cifar10_test(batch_size: int = DEFAULT_BATCH_SIZE):
    testset = CIFAR10(
        "./dataset", train=False, download=True, transform=transform_cifar10
    )
    testloader = DataLoader(testset, batch_size=batch_size)

    return testloader


def mnist_iid(
    client_id: int = 0, num_clients: int = 0, batch_size: int = DEFAULT_BATCH_SIZE
):
    """Load IID MNIST (training and test set)."""
    trainset = MNIST("./dataset", train=True, download=True, transform=transform_mnist)

    return dataset_iid(
        trainset, client_id=client_id, num_clients=num_clients, batch_size=batch_size
    )


def mnist_noniid(
    client_id: int = 0, num_clients: int = 0, batch_size: int = DEFAULT_BATCH_SIZE
):
    """Load non-IID MNIST (training and test set)."""
    trainset = MNIST("./dataset", train=True, download=True, transform=transform_mnist)
    return dataset_noniid(
        trainset,
        MNIST_SHARDS,
        client_id=client_id,
        num_clients=num_clients,
        batch_size=batch_size,
    )


def mnist_test(batch_size: int = DEFAULT_BATCH_SIZE):
    testset = MNIST("./dataset", train=False, download=True, transform=transform_mnist)
    testloader = DataLoader(testset, batch_size=batch_size)

    return testloader
