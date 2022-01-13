import numpy as np
from matplotlib import pyplot as plt

from ..models.utils import get_device

CIFAR_CLASSES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]
MNIST_CLASSES = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
FASHION_MNIST_CLASSES = [
    "T-Shirt",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle Boot",
]


def show_predictions(
    model,
    test_loader,
    channels=3,
    img_size=32,
    num_samples=6,
    labels=None,
    device=get_device(),
):
    xs, ys = iter(test_loader).next()
    preds = model(xs.to(device)).detach().cpu()

    _, axs = plt.subplots(1, num_samples, figsize=(24, 8))
    for i in range(num_samples):
        ax = axs[i]
        ax.set_xticks([]), ax.set_yticks([])
        if labels:
            ax.set_xlabel(
                f"prediction: {labels[np.argmax(preds[i])]}, actual: {labels[ys[i]]}"
            )
        ax.imshow(
            np.transpose(xs[i].reshape((channels, img_size, img_size)), (1, 2, 0))
        )
