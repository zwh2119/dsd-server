import torch.fft
from torch import Tensor, nn

import utils


class FeedForwardModel(nn.Module):
    def __init__(self, hidden_size: int, num_labels: int = 6):
        super(FeedForwardModel, self).__init__()
        self.norm = nn.BatchNorm1d(utils.data_size)
        self.transform = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.predict = nn.Sequential(
            nn.Linear(hidden_size * utils.window_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Linear(hidden_size, num_labels)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        inputs = self.norm(inputs.transpose(-1, -2)).transpose(-1, -2)
        inputs = torch.fft.fft(inputs, norm='forward', dim=-1)
        inputs = torch.cat([inputs.real, inputs.imag], dim=-1)
        return self.predict(self.transform(inputs).flatten(-2))


class RNNModel(nn.Module):
    def __init__(self, hidden_size: int, num_labels: int = 6):
        super(RNNModel, self).__init__()
        self.norm = nn.BatchNorm1d(utils.data_size)
        self.transform = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.predict = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Linear(hidden_size, num_labels)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        inputs = self.norm(inputs.transpose(-1, -2)).transpose(-1, -2)
        rnn_hidden = self.gru(self.transform(inputs))
        return self.predict(rnn_hidden[1][0])


class HybridModel(nn.Module):
    def __init__(self, hidden_size: int, kernel_size: int = 4, num_labels: int = 6):
        super(HybridModel, self).__init__()
        self.cnn = nn.Sequential(
            nn.BatchNorm1d(hidden_size),
            nn.Conv1d(hidden_size, hidden_size, kernel_size),
            nn.ReLU(),
        )
        self.rnn = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.predict = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Linear(hidden_size, num_labels)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        cnn_hidden = self.cnn(inputs.transpose(-1, -2)).transpose(-1, -2)
        rnn_hidden = self.rnn(cnn_hidden)
        return self.predict(rnn_hidden[1][0])
