################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

# Swap isn't ready yet for this to work, but this is the general
# outline of how server is going to interact with DB and SWAP

from swap import SWAP
from swap.mongo import DB
from swap.mongo import Query
from swap.mongo import Group
from pprint import pprint

class Server:

    def __init__(self, p0, epsilon):
        self._db = DB()
        self.classifications = self._db.classifications
        self.subjects = self._db.subjects

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
        fields = ['user_id', 'classification_id', 'subject_id', \
                  'annotation', 'gold_label', \
                  ('probability', self.epsilon)]
        q = Query()
        q.project(fields).limit(5)


        classifications = self.classifications.aggregate(q.build())


        return classifications

    def getClassificationsByUser(self):
        q = Query()
        g = Group().id('user_id').push('classifications',['classification_id','subject_id','annotation'])
        q.group(g).match('_id','',False).limit(5)

        print(q.build())

        users = self.classifications.aggregate(q.build(),allowDiskUse=True)

        return users



    def getSubjects(self):
        """
            Gets subject data from previously created
            subject collection
        """
        q = Query()
        q.limit(5)

        subjects = self.subjects.aggregate(q.build())

        return subjects

    def getSubjects_aggregate(self):
        """
            Generates subject data by aggregating
            from classifications
        """
        fields = ['subject_id','gold_label','diff']
        project = {'_id': '$_id.subject_id', \
                   'gold_label': '$_id.gold_label', \
                   'diff':'$_id.diff'}

        q = Query()
        q.group(fields).project(project)

        subjects = self.classifications.aggregate(q.build())

        return subjects

