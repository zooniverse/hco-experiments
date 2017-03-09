################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

import progressbar

from swap.swap import SWAP
from swap.mongo import DB
from swap.mongo import Query
from swap.config import Config


class Control:

    def __init__(self, p0, epsilon):
        self._db = DB()
        self._cfg = Config()
        self.classifications = self._db.classifications
        self.subjects = self._db.subjects
        self.swap = SWAP(p0, epsilon)

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

        n_class = 0
        with progressbar.ProgressBar(max_value=n_classifications) as bar:
            # Loop over all classifications of the query
            # Note that the exact size of the query might be lower than
            # n_classifications if not all classifications are being queried
            for current_classification in classifications:
                # process classification in swap
                self.swap.processOneClassification(current_classification)
                bar.update(n_class)
                n_class += 1
                # if i % 100e3 == 0:
                #     print("   " + str(i) + "/" + str(n_classifications))
            print("Finished: SWAP Processing %d/%d classifications" %
                  (n_class, n_classifications))

    def getSWAP(self):
        """ Returns SWAP object """
        return self.swap

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
        classifications = self.classifications.aggregate(q.build())

        return classifications
