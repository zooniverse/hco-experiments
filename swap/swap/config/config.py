################################################################
# Configuration module to handle local config setup

from swap.config.helpers import Singleton


class Object:
    def __init__(self, obj):
        if type(obj) is dict:
            for key, value in obj.items():
                if type(value) is dict:
                    value = Object(value)
                setattr(self, key, value)


class _Config:
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

    p0 = 0.12
    epsilon = 0.5

    database = Object({
        'name': 'swapDB',
        'host': 'localhost',
        'port': 27017,
        'max_batch_size': 1e5,
        'metadata': ['mag', 'mag_err'],
    })


class Config(_Config, metaclass=Singleton):
    pass
