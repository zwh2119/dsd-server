import sys
from abc import abstractmethod

import utils


class PredictorBase:
    def __init__(self, model):
        self.model = model
        self.queue = list()

    def predict(self):
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
            self.queue.append(x)

            if len(self.queue) < utils.window_size:
                continue

            print(self.get_label())
            self.queue.pop(0)

    @abstractmethod
    def get_label(self):
        pass

    def __call__(self):
        return self.predict()
