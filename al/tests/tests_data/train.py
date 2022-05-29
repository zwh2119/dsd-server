from sklearn import naive_bayes

from utils import TrainParser
from utils.MLBase.trainer import Trainer

if __name__ == '__main__':
    parser = TrainParser()
    args = parser.parse_args()
    model = naive_bayes.GaussianNB()
    trainer = Trainer(model, **vars(args))
    trainer()
