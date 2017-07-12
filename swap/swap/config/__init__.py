
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
gamma = 5

# Retirement Thresholds
mdr = 0.1
fpr = 0.01

# Methodology
# Set this flag to true to use the back-updating transactional methodology
# Setting this flag to false uses the traditional SWAP methodology
back_update = False

# Operator used in controversial and consensus score calculation
controversial_version = 'pow'

# Activate debug mode for control
# limits how many classifications Control will iterate through
class control:
    debug = False
    amount = 100000


# Database config options
class database:
    name = 'caesarTest'
    host = 'localhost'
    port = 27017
    max_batch_size = 1e5

class parser:

    subject_metadata = {
        'subject': {'type': int, 'remap': ['subject_id']},
        'gold': {'type': int, 'remap': ['gold_label']},
        'object_id': {'type': int},
        'machine_score': {'type': float},
        'mag': {'type': float},
        'mag_err': {'type': float}
    }

    classification = {
        'classification_id': {'type': int, 'remap': {'json': 'id'}},
        'user_id': {'type': int},
        'annotation': {'type': int},
        'workflow': {'type': int, 'remap': 'workflow_id'},
        'subject_id': {'type': int, 'remap': {'csv': 'subject_ids'}},
        'seen_before':
            {'type': bool, 'remap': ['metadata.seen_before'], 'ifgone': False},
        'live_project': {'type': bool, 'remap': ['metadata.live_project']},
        'session_id': {'remap': ['metadata.session']},
        'time_stamp': {'type': 'timestamp', 'remap': 'created_at'},
    }

    _timestamp_format = [
        '%Y-%m-%d %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S.%fZ'
    ]

    class annotation:
        task = 'T1'
        value_key = None
        value_separator = '.'
        true = [1]
        false = [0]


class online_swap:
    # Flask app config
    host = 'northdown.spa.umn.edu'
    ext_port = '443'
    port = '5000'
    bind = '0.0.0.0'
    debug = False

    workflow = 2614

    class caesar:
        # Address configuration for accessing caesar
        host = 'caesar-staging.zooniverse.org'
        port = '443'

        # Authorization token for panoptes
        OAUTH = None
        # Response data for reductions
        reducer = 'swap'
        field = 'swap_score'

    class address:
        # Caesar URL format
        _base = 'https://%(host)s:%(port)s/workflows/%(workflow)s'
        _reducer = '/reducers/%(reducer)s/reductions'
        _swap = 'https://%(user)s:%(pass)s@%(host)s:%(port)s/classify'

        #     {
        #               extractors_config: {"ext": {"type": "external", "url": "https://user:pass@myserver.com"}},
        #               reducers_config: {"%(reducer)": {"type": "external"}},
        #               rules_config: []
        #             }
        #
        # {''}
        # workflow:

    _auth_username = 'caesar'
    _auth_key = 'A7z9z2KwRVt4jXhXvRDy753SbBjCLNBB'


class logging:
    file_format = '%(asctime)s:%(levelname)s::%(name)s:%(funcName)s ' + \
                  '%(message)s'
    console_format = '%(asctime)s %(levelname)s %(message)s'
    date_format = '%Y%m%d_%H:%M:%S'
    level = 'DEBUG'
    console_level = 'INFO'

    keep_logs = 5

    class files:
        version = 'dynamic'

        dynamic = 'swap-%(pid)d.log'
        static = 'swap.log'

        keep_logs = 5
        max_size_mb = 10

    class system:
        active = False
        location = '/var/log/online-swap'
        name = 'swap.log'
        keep = 10
        max_size = 10


class ConfigError(Exception):
    def __init__(self, item, value):
        super().__init__('Error parsing config entry %s: %s' %
                         (str(item), str(value)))


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
