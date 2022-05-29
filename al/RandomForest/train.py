from sklearn import ensemble

from utils import TrainParser
from utils.MLBase.trainer import Trainer

if __name__ == '__main__':
    parser = TrainParser()
    args = parser.parse_args()
    model = ensemble.RandomForestClassifier()
    trainer = Trainer(model, **vars(args))
    trainer()
