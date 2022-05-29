from sklearn import neighbors

from utils import TrainParser
from utils.MLBase.trainer import Trainer

if __name__ == '__main__':
    parser = TrainParser()
    args = parser.parse_args()
    model = neighbors.KNeighborsClassifier()
    trainer = Trainer(model, **vars(args))
    trainer()
