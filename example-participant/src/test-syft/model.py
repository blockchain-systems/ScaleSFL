import syft as sy


class MLP(sy.Module):
    def __init__(self, torch_ref):
        super().__init__(torch_ref=torch_ref)
        self.l1 = self.torch_ref.nn.Linear(28 * 28, 100)
        self.a1 = self.torch_ref.nn.ReLU()
        self.l2 = self.torch_ref.nn.Linear(100, 10)

    def forward(self, x):
        x_reshaped = x.view(-1, 28 * 28)
        l1_out = self.a1(self.l1(x_reshaped))
        l2_out = self.l2(l1_out)
        return l2_out
