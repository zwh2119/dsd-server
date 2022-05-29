import logging
import time

import joblib
from sklearn import metrics
from torch.utils.data import DataLoader

import utils
from utils import CustomDataset

logger = logging.getLogger("north_star")


class Trainer:
    def __init__(self, model, epochs: int, data_file: str, out_model_file: str, in_model_file: str = None, debug: bool = False):
        self.epochs: int = epochs
        self.data_file = data_file
        self.out_model_file: str = out_model_file
        self.model = model
        if in_model_file is not None:
            self.model = joblib.load(in_model_file)
        self.debug = debug

    def train(self):
        X, Y = self.get_train_dataloader()
        train_start = time.perf_counter()
        self.model.fit(X, Y)
        train_end = time.perf_counter()
        print(train_end - train_start)
        joblib.dump(self.model, self.out_model_file)

        if self.debug:
            X, golds = self.get_eval_dataloader()
            test_start = time.perf_counter()
            predicts = self.model.predict(X)
            test_end = time.perf_counter()
            print(test_end - test_start)
            logger.info("\n" + metrics.classification_report(golds, predicts))
            logger.info("\n" + str(metrics.confusion_matrix(golds, predicts)))

    def get_train_dataloader(self):
        dataset = CustomDataset(self.data_file, window_size=utils.window_size)
        dataloader = DataLoader(dataset, batch_size=len(dataset) // 10, shuffle=True)
        X, Y = next(iter(dataloader))
        X = X.reshape(len(dataset) // 10, -1).numpy()
        return X, Y

    @staticmethod
    def get_eval_dataloader():
        dataset = CustomDataset('../eval', window_size=utils.window_size)
        dataloader = DataLoader(dataset, batch_size=len(dataset), shuffle=True)
        X, Y = next(iter(dataloader))
        X = X.reshape(len(dataset), -1).numpy()
        return X, Y

    def __call__(self):
        return self.train()
