
"""
    Globally accessible config object. All variables that are specific
    to a project should be in here.

    Config is a singleton class. To access its variables, for example
    to access p0, do::
        import swap.config as config
        config.p0
"""


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
database = Object({
    'name': 'swapDB',
    'host': 'localhost',
    'port': 27017,
    'max_batch_size': 1e5,
    'metadata': ['mag', 'mag_err'],
})

logging = Object({
    'file_format': '%(asctime)s:%(levelname)s::%(name)s:%(funcName)s ' +
                   ' %(message)s',
    'console_format': '%(asctime)s %(levelname)s %(message)s',
    'date_format': '%Y%m%d_%H:%M:%S',
    'level': 'DEBUG',
    'console_level': 'INFO',
    'keep_logs': 5,
    'filename': 'swap-%d.log'
})
