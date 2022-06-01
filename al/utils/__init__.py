import logging

from .argparser import *
from .dataset import *

window_size: int = 20
data_size: int = 45
batch_size: int = 32

label2idx = {
    'sit': 0,
    'stand': 1,
    'walk': 2,
    'upstairs': 3,
    'downstairs': 4,
    'run': 5
}
idx2label = dict(zip(label2idx.values(), label2idx.keys()))

# logger
logger = logging.getLogger("north_star")
logger.setLevel(logging.INFO)
log_format = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")

file_handler = logging.FileHandler(f"runtime.log")
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)
