import joblib
import numpy as np

import utils
from utils.predict import PredictorBase


class Predictor(PredictorBase):
    def __init__(self, model, in_model_file: str):
        super().__init__(model)
        if in_model_file is not None:
            self.model = joblib.load(in_model_file)

    def get_label(self):
        sample = np.array(self.queue)
        sample = np.reshape(sample, (1, -1))

        return utils.idx2label[self.model.predict(sample).item()]

    def __call__(self):
        return self.predict()
