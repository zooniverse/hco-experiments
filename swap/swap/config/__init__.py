
"""
    Globally accessible config object. All variables that are specific
    to a project should be in here.

    Config is a singleton class. To access its variables, for example
    to access p0, do::
        import swap.config as config
        config.p0
"""

import os
import sys
import importlib.util


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


# Prior probabilities
p0 = 0.12
epsilon = 0.5

# Retirement Thresholds
mdr = 0.1
fpr = 0.01

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

    class builder:

        subject_metadata = {
            'subject_id': int,
            'gold': (int, 'gold_label'),
            'object_id': int,
            'machine_score': float,
            'mag': float,
            'mag_err': float
        }

        _core_types = {
            'classification_id': (int, ('classification_id', 'id')),
            'user_id': int,
            'annotation': int,
            'workflow': int,
            # 'gold_label': int,
            'subject_id': (int, 'subject_ids'),
            'seen_before': bool,
            'live_project': bool,
            'time_stamp': 'timestamp',
        }

        _timestamp_format = [
            '%Y-%m-%d %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ]

        class annotation:
            task = 'T0'
            value_key = 'details.0.value.0'
            value_separator = '.'
            true = ['Real', 'yes', 1]
            false = ['Bogus', 'no', 0]


class online_swap:
    # Flask app config
    port = '5000'
    bind = '0.0.0.0'
    debug = False

    workflow = 1737

    class caesar:
        # Address configuration for accessing caesar
        host = 'localhost'
        port = '3000'
        # Authorization token for panoptes
        OAUTH = None
        # Response data for reductions
        reducer = 'swap'
        field = 'swap_score'

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

    class system:
        active = False
        location = '/var/log/online-swap'
        name = 'online-swap.log'
        keep_logs = 10
        max_size = '20M'


def local_config():
    # Import local_config.py to seamlessly override
    # config defaults without having to check in to git repo
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'config.py')
    if os.path.isfile(path):
        # pylint: disable=E0401,W0401
        import_config(path)


def module():
    return sys.modules[__name__]


def import_config(path):
    """
    Import a custom fon
    """
    spec = importlib.util.spec_from_file_location('module', path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    foo.override(module())


local_config()
