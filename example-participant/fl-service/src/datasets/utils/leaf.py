import os
import json
from functools import lru_cache
from collections import defaultdict

import numpy as np
from torch.utils.data import Dataset


class FEMNIST(Dataset):
    def __init__(
        self, data_dir, client_id=0, train=True, transform=None, target_transform=None
    ):
        data_dir = os.path.join(data_dir, "train" if train else "test")
        clients, _, img_data = read_leaf_dir(data_dir)
        self.client_id = clients[client_id]
        self.img_data = np.array(img_data[self.client_id]["x"]).reshape(-1, 1, 28, 28)
        print(self.img_data)
        self.img_labels = np.array(img_data[self.client_id]["y"])

        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        image = self.img_data[idx]
        label = self.img_labels[idx]
        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        return image, label


#
# Leaf https://github.com/TalwalkarLab/leaf/blob/master/models/utils/model_utils.py
#


@lru_cache
def read_leaf_dir(data_dir):
    clients = []
    groups = []
    data = defaultdict(lambda: None)

    files = os.listdir(data_dir)
    files = [f for f in files if f.endswith(".json")]
    for f in files:
        file_path = os.path.join(data_dir, f)
        with open(file_path, "r") as inf:
            cdata = json.load(inf)
        clients.extend(cdata["users"])
        if "hierarchies" in cdata:
            groups.extend(cdata["hierarchies"])
        data.update(cdata["user_data"])

    clients = list(sorted(data.keys()))
    return clients, groups, data
