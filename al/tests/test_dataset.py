import os

import pytest

import utils


class TestCustomDataset:
    @classmethod
    def setup_class(cls):
        os.mkdir('./empty_directory')

    @classmethod
    def teardown_class(cls):
        os.rmdir('./empty_directory')

    def test_directory_not_exist(self):
        with pytest.raises(FileNotFoundError) as _:
            utils.CustomDataset.spawn('./not_exist')

    def test_empty_directory(self):
        with pytest.raises(RuntimeError, match="Directory do not have valid data files!") as _:
            utils.CustomDataset.spawn('./empty_directory')

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("I_don't_know_what_is_this?", None),
            ("La,la,la,la,i,love,you", None),
            ("ABC?", None),
            ("145119195156", None),
            ("acs_downstairs_01", "downstairs"),
            ("dlf_run_01", "run"),
            ("dlf_upstairs_02.csv", "upstairs"),
            ("dlf_walk_041", "walk"),
            ("sjj_sit", "sit"),
            ("sjj_stand", "stand")
        ]
    )
    def test_get_motion(self, test_input: str, expected: str):
        assert utils.CustomDataset.get_motion(test_input) == expected
