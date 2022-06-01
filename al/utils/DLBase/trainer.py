import logging

import torch
from accelerate import Accelerator
from sklearn import metrics
from torch import nn
from torch.nn import functional
from torch.utils.data import DataLoader
from tqdm import tqdm

import utils
from utils import CustomDataset

logger = logging.getLogger("north_star")


class Trainer:
    def __init__(
            self,
            model: nn.Module,
            epochs: int,
            data_file: str,
            out_model_file: str,
            in_model_file: str = None,
            debug: bool = False
    ):
        self.total_steps = None

        self.epochs: int = epochs

        self.out_model_file: str = out_model_file

        if in_model_file is not None:
            map_location = torch.device("cpu") if not torch.cuda.is_available() else None
            model.load_state_dict(torch.load(in_model_file, map_location=map_location))
        optimizer = self.create_optimizer(model)

        train_dataloader = self.get_train_dataloader(data_file, utils.batch_size)

        self.accelerator = Accelerator()
        self.model, self.optimizer = self.accelerator.prepare(model, optimizer)
        self.train_dataloader = self.accelerator.prepare(train_dataloader)

        if debug:
            eval_dataloader = self.get_eval_dataloader(32)
            self.eval_dataloader = self.accelerator.prepare(eval_dataloader)

        self.debug = debug

    def train(self):
        for epoch_index in range(self.epochs):
            with tqdm(total=len(self.train_dataloader), desc=f"Epoch {epoch_index}") as tbar:
                self.model.train()
                for batch_index, [data, gold] in enumerate(self.train_dataloader):
                    self.optimizer.zero_grad()

                    prediction = self.model(data)
                    loss = functional.cross_entropy(prediction, gold, label_smoothing=0.5)
                    self.accelerator.backward(loss)
                    self.optimizer.step()

                    tbar.set_postfix(loss=loss.item())
                    tbar.update()

            if self.debug:
                with torch.no_grad():
                    self.model.eval()
                    predicts, golds = [], []
                    for batch_index, [data, gold] in enumerate(self.eval_dataloader):
                        predicts += self.model(data).argmax(dim=1).tolist()
                        golds += gold.tolist()

                    logger.info("\n" + metrics.classification_report(golds, predicts))
                    logger.info("\n" + str(metrics.confusion_matrix(golds, predicts)))

        torch.save(self.model.state_dict(), self.out_model_file)

    @staticmethod
    def create_optimizer(model: nn.Module):
        return torch.optim.AdamW(model.parameters(), lr=3e-4)

    def get_train_dataloader(self, data_file: str, batch_size: int):
        train_dataset = CustomDataset(data_file, window_size=utils.window_size)
        self.total_steps = (len(train_dataset) // utils.batch_size + 1) * self.epochs
        return DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    @staticmethod
    def get_eval_dataloader(batch_size: int):
        eval_dataset = CustomDataset('../eval', window_size=utils.window_size)
        return DataLoader(eval_dataset, batch_size=batch_size, shuffle=True)

    def __call__(self):
        return self.train()
