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
    def addOne(self, item):
        pass

    @abstractmethod
    def addMany(self, items):
        pass

    @abstractmethod
    def getItems(self, **kwargs):
        pass

    @abstractmethod
    def getAllItems(self):
        pass
