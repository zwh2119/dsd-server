import io
import sys
import time

import pytest
from sklearn import metrics, naive_bayes
from torch.utils.data import DataLoader

import utils
from utils.MLBase.predictor import Predictor
from utils.MLBase.trainer import Trainer
from utils.dataset import CustomDataset


# to test the models, in my point of view we can't execute unit tests because we will be dependent of the other modules that can be tested like
# (utils module methods) or external models like sklearn etc.
# 
# So I talk with professor Mestre and he advised to do tests to the models based on the metrics that the model give, about the execution time(more necessary 
# in the prediction) and test the predictions. All this with a dataset specific for the tests where we know the input and the expected output.
# So I get 2 or 3 csv files from the eval folder. 
# 
# You have data that was never used in training??? Is the data in eval ??   
# I simply used your code from the debug part of the MLBASE code.
#
#
#
# # NOTE: ( 1 ) In the MLBase.predict you simulate the stdin entrace, right? That is part of tests. The input should be like in specification.
# This way I can test and simulate the test inputs. 
# 
## NOTE: ( 2 ) In the MLBase.predict the output is only printed?? does not need to be sent to anywhere?
class TestMLBaseNaiveBayes:
    # Test the accuracy after training the model
    # I defined the accuracy of the model should be major than 0.8
    def test_accuracy_model(self):
        model = naive_bayes.GaussianNB()
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
        model = naive_bayes.GaussianNB()
        test_start = time.perf_counter()
        trainer = Trainer(model, data_file="data", out_model_file='tests/parameters.pt', epochs=20, debug=False)

        trainer()
        test_end = time.perf_counter()

        time_spent = test_end - test_start
        # print("Time End:",test_start)
        # print("Time Start:",test_end)
        print("Time:", time_spent)
        assert time_spent < 6

    # Test the time of prediction a motion
    #
    # Predictor code needs to be changed( 1 )
    def test_time_predict(self):
        model = naive_bayes.GaussianNB()
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
        model = naive_bayes.GaussianNB()
        predictor = Predictor(model, "parameters.pt")
        stdin = sys.stdin
        sys.stdin = open('tests/tests_data/test_wrong_format.csv', 'r')

        with pytest.raises(ValueError) as _:
            predictor()

        sys.stdin = stdin

    # Test when the input values have different lenghts.
    # Predictor code needs to be changed( 1 )

    def test_predictor_wrong_input_lenght(self):
        model = naive_bayes.GaussianNB()
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
        model = naive_bayes.GaussianNB()
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
