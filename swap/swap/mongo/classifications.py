################################################################
# Classification database interface

"""
    Current collection field configuration. This is 
    straight from the csv that Darryl shared on Slack:

    classifications:
        _id
        #classification_id
        user_name
        user_id
        annotation
        gold_label
        subject_id
        diff
        object_id
        machine_score <<<< Is this an artifact 
                           from previous processing?

    I propose the following structure for the main classifications
    collection. This would take a little bit of preprocessing when
    inserting the data, but might make it easier to aggregate later on:

    classifications:
        _id
        #classification_id
        user:
            user_name
            user_id
        classification:
            annotation
            gold_label
            subject_id
            diff
            object_id
        machine_score
"""

from swap.mongo.collection import Collection
from swap.config import Config

class Classifications(Collection):
    """
        Classifications

        Handles calls to classification collection
    """
    
    def __init__(self, db):
        config = Config()
        name = 'classifications'

        self.config = config
        self.collection = getattr(db, name)

    def addOne(self, item):
        result = self.collection.insert_one(item)

    def addMany(self, items):
        self.collection.insert_many(items)

    def getItems(self, **kwargs):
        return self.collection.find(kwargs)

    def getAllItems(self):
        return self.collection.find({})

    def drop(self):
        self.collection.drop()
