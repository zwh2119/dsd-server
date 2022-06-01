import torch
from torch import nn

import utils
from utils.predict import PredictorBase


class Predictor(PredictorBase):
    def __init__(self, model: nn.Module, in_model_file: str):
        super().__init__(model)
        self.model.load_state_dict(torch.load(in_model_file))

    def get_label(self):
        sample = torch.tensor(self.queue)
        return utils.idx2label[self.model(sample.unsqueeze(0)).argmax().item()]
