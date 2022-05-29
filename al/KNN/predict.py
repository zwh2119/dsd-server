import sklearn

from utils import PredictParser
from utils.MLBase import Predictor

if __name__ == '__main__':
    parser = PredictParser()
    args = parser.parse_args()
    model = sklearn.neighbors.KNeighborsClassifier()
    predictor = Predictor(model, **vars(args))
    predictor()
