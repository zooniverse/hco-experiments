################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

# Swap isn't ready yet for this to work, but this is the general
# outline of how server is going to interact with DB and SWAP

from swap import SWAP
from swap.mongo import DB
from swap.mongo import Query
from pprint import pprint

class Server:

    def __init__(self, p0, epsilon):
        self._db = DB()
        self.collection = self._db.classifications

        self.p0 = p0
        self.epsilon = epsilon

    def process(self):
        data = self.getData()
        swap = SWAP("Args passed to swap")

    def getData(self):
        subjects = self.getSubjects()
        classifications = self.getClassifications()
        return {'classifications': classifications, 'subjects': subjects}

    def getClassifications(self):
        fields = {'user_id', 'classification_id', 'subject_id', \
                  'annotation', 'gold_label'}
        q = Query()
        q.fields(fields).limit(5)


        raw = self.collection.aggregate(q.build())

        pprint(list(raw))

        for item in classifications:
                item['probability'] = self.epsilon

        return classifications

    def getSubjects(self):
        raw = self.collection.getDistinctSet('subject_id')
        subjects = {}
        for subject in raw:
            subjects[subject] = self.p0

        return subjects

