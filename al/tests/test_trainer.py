import os

import pytest

import utils


class TestTrainer:
    @classmethod
    def setup_class(cls):
        os.mkdir('./empty_directory')

    @classmethod
    def teardown_class(cls):
        os.rmdir('./empty_directory')

    def test_trainer(self):
        with pytest.raises(FileNotFoundError) as _:
            utils.Trainer(10, "./not_exist", "nothing", "nothing")
        with pytest.raises(RuntimeError, match="Directory do not have valid data files!") as _:
            utils.Trainer(10, "./empty_directory", "nothing", "nothing")
