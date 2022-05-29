from torch import Tensor, nn


class RNNModel(nn.Module):
    def __init__(self, hidden_size: int, num_layers: int = 1, num_labels: int = 6):
        super(RNNModel, self).__init__()
        self.transform = nn.Linear(hidden_size, hidden_size)
        self.rnn = nn.GRU(input_size=hidden_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.predict = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.GELU(),
            nn.Linear(hidden_size // 4, num_labels)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        rnn_hidden = self.rnn(self.transform(inputs))
        return self.predict(rnn_hidden[1][0])


class HybridModel(nn.Module):
    def __init__(self, hidden_size: int, kernel_size: int = 2, num_layers: int = 1, num_labels: int = 6):
        super(HybridModel, self).__init__()
        self.cnn = nn.Conv1d(hidden_size, hidden_size, kernel_size, kernel_size)
        self.rnn = nn.GRU(input_size=hidden_size, hidden_size=hidden_size, num_layers=num_layers, batch_first=True)
        self.predict = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 4),
            nn.GELU(),
            nn.Linear(hidden_size // 4, num_labels)
        )

    def forward(self, inputs: Tensor) -> Tensor:
        rnn_hidden = self.rnn(self.cnn(inputs.transpose(-1, -2)).transpose(-1, -2))
        return self.predict(rnn_hidden[1][0])
