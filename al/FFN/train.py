import utils
from utils import DLBase

if __name__ == '__main__':
    parser = utils.TrainParser()
    model = DLBase.FeedForwardModel(utils.data_size)
    trainer = DLBase.Trainer(model, **vars(parser.parse_args()))
    trainer()
