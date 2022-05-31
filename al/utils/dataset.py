import os
from typing import Optional

import pandas as pd
import torch
from torch.utils.data import Dataset
from tqdm import tqdm

import utils


class CustomDataset(Dataset):
    def __init__(self, data_directory_path: str, window_size: int):
        self.window_size: int = window_size

        data_paths = os.listdir(data_directory_path)
        data_paths = list(filter(lambda p: p.endswith('.csv') and self.get_motion(p), data_paths))
        if len(data_paths) == 0:
            raise RuntimeError("Directory do not have valid data files!")

        data_paths = list(map(lambda p: os.path.join(data_directory_path, p), data_paths))

        self.samples, self.golds = [], []
        for path in tqdm(data_paths, desc='Reading data'):
            idx = utils.label2idx[self.get_motion(path)]
            sample = torch.as_tensor(pd.read_csv(path, header=None).values, dtype=torch.float)
            self.samples.append(sample)
            self.golds.append(idx)
        self.length = [0] + [sample.shape[0] - self.window_size + 1 for sample in self.samples]
        for i in range(1, len(self.length)):
            self.length[i] += self.length[i - 1]

    @staticmethod
    def spawn(*args, **kargs):
        return CustomDataset(*args, **kargs)

    def get_sample_index(self, idx: int) -> int:
        l, r = 0, len(self.length)
        while l + 1 < r:
            m = (l + r) // 2
            if idx < self.length[m]:
                r = m
            else:
                l = m
        if l >= len(self.length) or l < 0:
            raise RuntimeError("Invalid index!")
        return l

    def __len__(self):
        return self.length[-1]

    def __getitem__(self, index: int):
        sample_index = self.get_sample_index(index)
        start = 0 if sample_index == 0 else index - self.length[sample_index]
        sample = self.samples[sample_index][start: start + self.window_size]
        gold = self.golds[sample_index]
        if sample.shape[-1] == 45:
            return sample, gold
        return torch.cat([sample[:, :30], sample[:, 75:]], dim=-1), gold

    @staticmethod
    def get_motion(pathname: str) -> Optional[str]:
        for name in list(utils.label2idx.keys()):
            if name in pathname:
                return name
        return None
