################################################################
# Collection abstract class

from abc import ABC, abstractmethod

class Collection(ABC):
    """
        Collection

        Abstract class describing the functionality
        the collection subclasses should implement
    """

    @abstractmethod
    def __init__(self, db):
        pass

    @abstractmethod
    def addItem(self, item):
        pass

    @abstractmethod
    def addItems(self, items):
        pass

    @abstractmethod
    def getItem(self, **kwargs):
        pass

    @abstractmethod
    def getAll(self):
        pass
