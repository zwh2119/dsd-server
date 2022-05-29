import argparse


class TrainParser(argparse.ArgumentParser):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.add_argument("data_file", nargs='?', type=str, default='../data')
        self.add_argument('out_model_file', nargs='?', type=str, default='parameters.pt')
        self.add_argument('in_model_file', nargs='?', type=str, default=None)
        self.add_argument('--epochs', type=int, default=5)
        self.add_argument('--debug', action='store_true', default=True)


class PredictParser(argparse.ArgumentParser):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.add_argument('in_model_file', nargs='?', type=str, default='parameters.pt')
