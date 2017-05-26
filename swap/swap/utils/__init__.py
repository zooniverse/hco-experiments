
from swap.utils.classification import Classification

assert Classification


class Singleton(type):
    """
    Singleton construct. Add as metaclass inheritance to only
    allow one instance of a class to exist. Currently used for
    DB and Config so that there is a single config instance,
    and a single connection to the database.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls)\
                .__call__(*args, **kwargs)
        return cls._instances[cls]

    def _reset_instances(cls):
        cls._instances = {}
