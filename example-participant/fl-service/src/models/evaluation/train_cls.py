import torch
from torch import nn
import torch.nn.functional as F
from opacus.privacy_engine import PrivacyEngine

from ..utils import DEVICE
from ...utils.constants import (
    DEFAULT_LEARNING_RATE,
    DEFAULT_LOCAL_EPOCHS,
    DEFAULT_MOMENTUM,
    PRIVACY_MAX_GRAD_NORM,
    PRIVACY_NOISE_MULTIPLIER,
)


def train(
    net,
    trainloader,
    epochs=DEFAULT_LOCAL_EPOCHS,
    lr=DEFAULT_LEARNING_RATE,
    momentum=DEFAULT_MOMENTUM,
    privacy_engine: PrivacyEngine = None,
    device=DEVICE,
):
    """Train the network on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=lr, momentum=momentum)
    loss_vals = []

    # Must be in training mode prior to wrapping Opacus
    net.train()
    # Apply DP if given privacy engine
    if privacy_engine:
        net, optimizer, trainloader = privacy_engine.make_private(
            module=net,
            optimizer=optimizer,
            data_loader=trainloader,
            noise_multiplier=PRIVACY_NOISE_MULTIPLIER,
            max_grad_norm=PRIVACY_MAX_GRAD_NORM,
        )

    for _ in range(epochs):
        epoch_loss = []
        for images, labels in trainloader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()

            epoch_loss.append(loss.item())

        loss_vals.append(sum(epoch_loss) / len(epoch_loss))

    # Cleanup hooks
    if privacy_engine:
        net.remove_hooks()

    return loss_vals


def test(net, testloader, device=DEVICE):
    """Validate the network on the entire test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, total, loss = 0, 0, 0.0
    net.eval()
    with torch.no_grad():
        for images, labels in testloader:
            images, labels = images.to(device), labels.to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    loss /= len(testloader.dataset)
    accuracy = correct / total
    return loss, accuracy
