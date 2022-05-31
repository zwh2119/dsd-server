import codecs
import sys

import utils
from utils import DLBase

sys.stdin = codecs.open("../output.csv", encoding='utf-16')
if __name__ == "__main__":
    parser = utils.PredictParser()
    model = DLBase.RNNModel(utils.data_size)
    predictor = DLBase.Predictor(model, **vars(parser.parse_args()))
    predictor()
