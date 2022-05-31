from sklearn import svm

from utils import TrainParser
from utils.MLBase.trainer import Trainer

if __name__ == '__main__':
    parser = TrainParser()
    args = parser.parse_args()
    # model = SGDClassifier(loss="hinge")
    model = svm.SVC(gamma='scale')
    trainer = Trainer(model, **vars(args))
    trainer()
