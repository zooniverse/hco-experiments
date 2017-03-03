################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

from pprint import pprint
import sys
import progressbar

from swap.swap import SWAP_AGENTS
from swap.mongo import DB
from swap.mongo import Query
from swap.mongo import Group
from swap.config import Config


class Control:

    def __init__(self, p0, epsilon):
        self._db = DB()
        self._cfg = Config()
        self.classifications = self._db.classifications
        self.subjects = self._db.subjects
        self.swap = SWAP_AGENTS(p0, epsilon)

    def process(self):
        """ Process all classifications in DB with SWAP

        Notes:
        ------
            Iterates through the classification collection of the
            database and proccesss each classification one at a time
            in the order returned by the db.
            Parameters like max_batch_size are hard-coded.
            Prints status.
        """
        # max batch size is the number classifications to read from DB
        # during one batch, small numbers (<1000) are inefficient
        max_batch_size = float(self._cfg.database['max_batch_size'])

        # get the total number of classifications in the DB
        n_classifications = self.classifications.count()

        # get classifications
        classifications = self.getClassifications()

        # determine and set batch size
        classifications.batch_size(int(min(max_batch_size, n_classifications)))

        # loop over classification cursor to process
        # classifications one at a time
        print("Start: SWAP Processing %d classifications" % n_classifications)

        with progressbar.ProgressBar(max_value=n_classifications) as bar:
            for i in range(0, n_classifications):
                # read next classification
                current_classification = classifications.next()
                # process classification in swap
                self.swap.processOneClassification(current_classification)

                bar.update(i)
                # if i % 100e3 == 0:
                #     print("   " + str(i) + "/" + str(n_classifications))
        print("Finished: SWAP Processing %d/%d classifications" %
              (i, n_classifications))

    def getSWAP(self):
        """ Returns SWAP object """
        return self.swap

    # def getData(self):
    #     subjects = self.getSubjects()
    #     classifications = self.getClassifications()
    #     return {'classifications': classifications, 'subjects': subjects}

    def getClassifications(self):
        """ Returns Iterator over all Classifications """

        # fields to project
        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']

        # Define a query
        q = Query()
        q.project(fields)

        # perform query on classification data
        classifications = self.classifications.aggregate(q.build())

        return classifications

    # def getUsers(self):

    #     g = Group()
    #     g.id('user_name')
    #     g.count()
    #     users = self.classifications.aggregate(g.build())
    #     return users

    # def getClassificationsByUser(self):
    #     q = Query()
    #     g = Group().id('user_id').push('classifications',['classification_id','subject_id','annotation'])
    #     q.group(g).match('_id','',False)

    #     print(q.build())

    #     users = self.classifications.aggregate(q.build(),allowDiskUse=True)

    #     return users

    # def getSubjects(self):
    #     """
    #         Gets subject data from previously created
    #         subject collection
    #     """
    #     q = Query()
    #     q.match('gold_label',1).limit(5)

    #     subjects = self.subjects.aggregate(q.build())

    #     return subjects

    # def getSubjects_aggregate(self):
    #     """
    #         Generates subject data by aggregating
    #         from classifications
    #     """
    #     fields = ['subject_id','gold_label','diff']
    #     project = {'_id': '$_id.subject_id', \
    #                'gold_label': '$_id.gold_label', \
    #                'diff':'$_id.diff'}

    #     q = Query()
    #     q.group(fields).project(project)

    #     subjects = self.classifications.aggregate(q.build())

    #     return subjects
