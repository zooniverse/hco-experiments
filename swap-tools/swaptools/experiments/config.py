
# pylint: disable=W0401,W0614
from swap.config import *

experiment_db = Object({
    'name': 'experimentsDB',
    'host': 'localhost',
    'port': 27017,
    'max_batch_size': 1e5,
})

trials = Object({
    'keep_amount': 10,
    'cutoff': 0.96
})
