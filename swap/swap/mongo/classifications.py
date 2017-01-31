################################################################
# Classifaction database interface

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
        machine_score <<<< Is this an artefact 
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

from swap.mongo import Collection
from swap.config import Config

class Classifications(Collection):
    """
        Classifications

        Handles calls to classification collection
    """
    
    def __init__(self, db):
        config = Config()
        name = config.database['collection']['classifications']

        self.config = config
        self.collection = getattr(db, name)

    def addItem(self, item):
        result = self.collection.insert_one(item)

    def addItems(self, items):
        self.collection.insert_many(items)

    def getItem(self, **kwargs):
        return self.collection.find(kwargs)

    def getAll(self):
        return self.collection.find({})

    def drop(self):
        self.collection.drop()
