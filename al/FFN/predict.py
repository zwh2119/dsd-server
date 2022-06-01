import utils
from utils import DLBase

if __name__ == "__main__":
    parser = utils.PredictParser()
    model = DLBase.FeedForwardModel(utils.data_size)
    predictor = DLBase.Predictor(model, **vars(parser.parse_args()))
    predictor()
