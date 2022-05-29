import sys

import torch
from torch import nn

import utils


class Predictor:
    def __init__(
            self,
            model: nn.Module,
            in_model_file: str
    ):
        self.model = model
        self.model.load_state_dict(torch.load(in_model_file))

    def predict(self):
        queue = []
        while True:
            x = sys.stdin.readline()
            if len(x) == 0:
                break
            try:
                x = [float(i) for i in x.split(',')]
            except ValueError as _:
                raise ValueError(f"Please check the input format, making sure it is separated by , in Ascii.")
            if len(x) != utils.data_size:
                raise RuntimeError(f"Unexpected data input length. Expected:{utils.data_size}")
            queue.append(x)

            if len(queue) < utils.window_size:
                continue

            sample = torch.tensor(queue)
            with torch.no_grad():
                print(utils.idx2label[self.model(sample.unsqueeze(0)).argmax().item()])
            queue.pop(0)

    def __call__(self):
        return self.predict()
