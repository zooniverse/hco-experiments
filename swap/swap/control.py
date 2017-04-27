################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

import progressbar

from swap.swap import SWAP, Classification
import swap.db.classifications as db
from swap.db import DB, Query
from swap.config import Config


class Control:
    """
        Gets classifications from database and feeds them to SWAP
    """

    def __init__(self, p0, epsilon, swap=None, train_size=None):
        self._cfg = Config()
        """
            Initialize control

            Args:
                p0:              prior subject probability
                epsilon: (float) initial user score
                train_size: (int) size of gold label sample for
                    test/train split
        """

        # Number of subjects with expert labels for a
        # test/train split
        self.train_size = train_size

        if swap is None:
            self.swap = self.initSwap(p0, epsilon)
        else:
            self.swap = swap

    def process(self):
        """
        Process all classifications in DB with SWAP

        Notes:
        ------
            Iterates through the classification collection of the
            database and proccesss each classification one at a time
            in the order returned by the db.
            Parameters like max_batch_size are hard-coded.
            Prints status.
        """

        # get classifications
        classifications = self.getClassifications()
        n_classifications = len(classifications)
        # n_classifications = self._n_classifications()

        # loop over classification cursor to process
        # classifications one at a time
        print("Start: SWAP Processing %d classifications" % n_classifications)

        n_class = 0
        with progressbar.ProgressBar(max_value=n_classifications) as bar:
            # Loop over all classifications of the query
            # Note that the exact size of the query might be lower than
            # n_classifications if not all classifications are being queried
            for cl in classifications:
                # process classification in swap
                cl = Classification.generate(cl)
                self._delegate(cl)
                bar.update(n_class)
                n_class += 1

    def _delegate(self, cl):
        """
        Method to allow subclasses to override how classifications
        are handed to swap

        cl: (Classification)
        """
        self.swap.processOneClassification(cl)

    def initSwap(self, p0, epsilon):
        swap = SWAP(p0, epsilon)

        golds = self.getGoldLabels()
        swap.setGoldLabels(golds)

        return swap

    def getGoldLabels(self):
        if self.train_size is None:
            cursor = db.getAllGolds()
        else:
            cursor = db.getRandomGoldSample(self.train_size)

        golds = []
        for item in cursor:
            golds.append((item['_id'], item['gold']))

        return golds

    def getClassifications(self):
        return db.getClassifications()

    def getSWAP(self):
        """ Returns SWAP object """
        return self.swap

    def setSWAP(self, swap):
        """
        Set the SWAP object
        """
        self.swap = swap


class MetaDataControl(Control):
    """ Calls SWAP to process classifications for specific meta data splits
    """

    def __init__(self, p0, epsilon, meta_data, meta_lower, meta_upper):
        # initialize control
        super().__init__(p0, epsilon)
        # meta data information
        self.meta_data = meta_data
        self.meta_lower = meta_lower
        self.meta_upper = meta_upper

    def getClassifications(self):
        """ Returns Iterator over all Classifications """

        # fields to project
        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']

        # if meta data is requested
        if self.meta_data is not None:
            meta_data_field = 'metadata' + "." + self.meta_data
            fields.append('metadata')
            fields[fields.index('metadata')] = meta_data_field

        # Define a query
        q = Query()
        q.project(fields)

        # range query on metadata
        if self.meta_lower is not None and self.meta_upper is not None:
            q.match_range(meta_data_field, self.meta_lower, self.meta_upper)

        # perform query on classification data
        classifications = db.aggregate(q.build())

        return classifications


class DummySWAP:
    def __init__(self):
        self.data = {}

    def process(self):
        cursor = self.get_cursor()
        for item in cursor:
            score = item['votes'] / item['total']
            gold = item['gold']
            subject = item['_id']
            self.data[subject] = (gold, score)

    def get_cursor(self):
        cursor = db.aggregate([
            {'$match': {'gold_label': {'$ne': -1}}},
            {'$group': {
                '_id': '$subject_id',
                'gold': {'$first': "$gold_label"},
                'total': {'$sum': 1},
                'votes': {'$sum': "$annotation"}}}])

        return cursor

    def export(self):
        data = {}
        for subject, item in self.data.items():
            data[subject] = {'gold': item[0], 'score': item[1]}

        return data

    def roc_export(self):
        data = []
        for item in self.data.values():
            data.append(item)

        return data
