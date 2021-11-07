import torch
from syft.core.plan.plan_builder import ROOT_CLIENT

from config import lr


def set_params(model, params):
    for p, p_new in zip(model.parameters(), params):
        p.data = p_new.data


def cross_entropy_loss(logits, targets, batch_size):
    norm_logits = logits - logits.max()
    log_probs = norm_logits - norm_logits.exp().sum(dim=1, keepdim=True).log()
    return -(targets * log_probs).sum() / batch_size


def sgd_step(model, lr=lr):
    with ROOT_CLIENT.torch.no_grad():
        for p in model.parameters():
            p.data = p.data - lr * p.grad
            p.grad = torch.zeros_like(p.grad.get())


def read_file(fname):
    with open(fname, "r") as f:
        return f.read()
