
"""
    Globally accessible config object. All variables that are specific
    to a project should be in here.

    Config is a singleton class. To access its variables, for example
    to access p0, do::
        import swap.config as config
        config.p0
"""

import os


class Object:
    """
    Accepts a dict as an argument. Sets an instance variable
    for each key value mapping in the dict
    """

    def __init__(self, obj):
        if type(obj) is dict:
            for key, value in obj.items():
                if type(value) is dict:
                    value = Object(value)
                setattr(self, key, value)


csv_types = {
    'classification_id': int,
    'user_id': int,
    'annotation': int,
    'gold_label': int,
    'subject_id': int,

    'machine_score': float,
    'mag': float,
    'mag_err': float
}

# Prior probabilities
p0 = 0.12
epsilon = 0.5

# Methodology
# Set this flag to true to use the back-updating transactional methodology
# Setting this flag to false uses the traditional SWAP methodology
back_update = False

# Operator used in controversial and consensus score calculation
controversial_version = 'pow'


# Database config options
class database:
    name = 'swapDB'
    host = 'localhost'
    port = 27017
    max_batch_size = 1e5
    metadata = ['mag', 'mag_err']


class caesar:
    # Address configuration for accessing caesar
    host = 'localhost'
    port = '3000'
    # Authorization token for panoptes
    OAUTH = None

    class response:
        # Response data for reductions
        workflow = '1737'
        reducer = 'swap'
        field = 'swap_score'

    class swap:
        # Flask app config
        port = '5000'
        bind = '0.0.0.0'
        debug = False

    # Caesar URL format
    _addr_format = 'http://%(host)s:%(port)s/workflows/%(workflow)s' + \
                   '/reducers/%(reducer)s/reductions'


class logging:
    file_format = '%(asctime)s:%(levelname)s::%(name)s:%(funcName)s ' + \
                  '%(message)s'
    console_format = '%(asctime)s %(levelname)s %(message)s'
    date_format = '%Y%m%d_%H:%M:%S'
    level = 'DEBUG'
    console_level = 'INFO'
    keep_logs = 5
    filename = 'swap-%d.log'


# Import local_config.py to seamlessly override
# config defaults without having to check in to git repo
path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(path, 'local_config.py')
if os.path.isfile(path):
    # pylint: disable=E0401,W0401
    from swap.config.local_config import *
