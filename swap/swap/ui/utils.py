
import pickle
import sys
import logging

logger = logging.getLogger(__name__)


def load_pickle(fname):
    """
        Loads a pickled object from file
    """
    try:
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        return data
    except Exception as e:
        logger.error('Error load file %s', fname)
        raise e


def save_pickle(object_, fname):
    """
        Pickles and saves an object to file
    """
    sys.setrecursionlimit(10000)
    with open(fname, 'wb') as file:
        pickle.dump(object_, file)


def write_log(swap, fname):
    with open(fname, 'w') as file:
        file.writelines(swap.debug_str())
