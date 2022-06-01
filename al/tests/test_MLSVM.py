import io
import sys
import time

import pytest
from sklearn import metrics, svm
from torch.utils.data import DataLoader

import utils
from utils.MLBase.predictor import Predictor
from utils.MLBase.trainer import Trainer
from utils.dataset import CustomDataset


class TestMLSVM:

    def test_accuracy_model(self):
        model = svm.SVC(gamma='scale')
        trainer = Trainer(model, data_file="data", out_model_file='tests/parameters.pt', epochs=20, debug=False)
        trainer()

        test_X, test_Y = self.get_test_dataloader()
        test_start = time.perf_counter()
        predicts = trainer.model.predict(test_X)
        test_end = time.perf_counter()
        accuracy = metrics.accuracy_score(predicts, test_Y)
        print("Accuracy:", accuracy)
        assert accuracy > 0.9

    # Test the time of training a model
    # defined maximum 1 second
    #
    def test_time_train(self):
        model = svm.SVC(gamma='scale')
        test_start = time.perf_counter()
        trainer = Trainer(model, data_file="data", out_model_file='tests/parameters.pt', epochs=20, debug=False)

        trainer()
        test_end = time.perf_counter()

        time_spent = test_end - test_start
        print("Time:", time_spent)
        assert time_spent < 6

    # Test the time of prediction a motion
    #
    # Predictor code needs to be changed( 1 )
    def test_time_predict(self):
        model = svm.SVC(gamma='scale')
        test_start = time.perf_counter()

        predictor = Predictor(model, "parameters.pt")
        stdin = sys.stdin
        sys.stdin = open('tests/tests_data/test_predict_time.csv', 'r')
        predictor()
        test_end = time.perf_counter()
        sys.stdin = stdin
        time_spent = test_end - test_start
        print("Time End:", test_start)
        print("Time Start:", test_end)
        print("Time:", time_spent)
        assert time_spent < 0.2
        # assert True

    # Test when the input values are changed.
    # Predictor code needs to be changed( 1 )
    def test_predictor_wrong_input_format(self):
        model = svm.SVC(gamma='scale')
        predictor = Predictor(model, "parameters.pt")
        stdin = sys.stdin
        sys.stdin = open('tests/tests_data/test_wrong_format.csv', 'r')

        with pytest.raises(ValueError) as _:
            predictor()

        sys.stdin = stdin

    # Test when the input values have different lenghts.
    # Predictor code needs to be changed( 1 )

    def test_predictor_wrong_input_lenght(self):
        model = svm.SVC(gamma='scale')
        predictor = Predictor(model, "parameters.pt")
        stdin = sys.stdin
        sys.stdin = open('tests/tests_data/test_wrong_lenght.csv', 'r')

        with pytest.raises(RuntimeError) as _:
            predictor()

        sys.stdin = stdin

    # Insert some inputs on the predictor and see if result is the expected like, done in another test:
    @pytest.mark.parametrize(
        "inputdata,expectedresult",
        [
            ("tests/tests_data/test_downstairs.csv", 'downstairs'),
            ("tests/tests_data/test_run.csv", 'run'),
            ("tests/tests_data/test_sit.csv", 'sit'),
            ("tests/tests_data/test_stand.csv", 'stand'),
            ("tests/tests_data/test_upstairs.csv", 'upstairs'),
            ("tests/tests_data/test_walk.csv", 'walk'),
        ]
    )
    def test_predictor_input_output(self, inputdata, expectedresult):
        model = svm.SVC(gamma='scale')
        predictor = Predictor(model, "parameters.pt")
        stdin = sys.stdin
        stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        sys.stdin = open(inputdata, 'r')
        predictor()
        sys.stdout = stdout
        value = buffer.getvalue()
        value = value.replace('\n', '')
        sys.stdin = stdin
        assert expectedresult == value

    # get test data
    def get_test_dataloader(self):
        dataset = CustomDataset('tests/tests_data/eval', window_size=utils.window_size)
        dataloader = DataLoader(dataset, batch_size=len(dataset), shuffle=True)
        X, Y = next(iter(dataloader))
        X = X.reshape(len(dataset), -1).numpy()
        return X, Y
