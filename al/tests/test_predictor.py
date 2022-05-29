import pytest

import utils


class TestPredictor:
    def test_trainer(self):
        with pytest.raises(FileNotFoundError) as _:
            utils.Trainer(10, "./not_exist", "nothing", "nothing")
