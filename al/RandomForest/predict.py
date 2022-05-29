from sklearn import ensemble

from utils import PredictParser
from utils.MLBase import Predictor

if __name__ == '__main__':
    parser = PredictParser()
    args = parser.parse_args()
    model = ensemble.RandomForestClassifier()
    predictor = Predictor(model, **vars(args))
    predictor()
