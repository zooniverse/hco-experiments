################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

"""
Contains classes to control a SWAP instance

    Control: Regular SWAP instance in simulation mode

    MetaDataControl: SWAP instance that splits data by metadata
"""

import swap.db.classifications as db
import swap.db
import swap.config as config
from swap.swap import SWAP
from swap.utils.classification import Classification
from swap.utils.golds import GoldGetter
from swap.db import Query

import progressbar
import logging
logger = logging.getLogger(__name__)


class Control:
    """
        Gets classifications from database and feeds them to SWAP
    """

    def __init__(self, *args):
        """
            Initialize control

            Args:
                p0:              (Deprecated) prior subject probability
                epsilon:         (Deprecated) initial user score
        """
        if len(args) > 0:
            raise DeprecationWarning(
                'p0 and epsilon now live in config')

        # Number of subjects with expert labels for a
        # test/train split
        self.gold_getter = GoldGetter()
        self.swap = None

    def run(self):
        """
        Process all classifications in DB with SWAP

        .. note::
            Iterates through the classification collection of the
            database and proccesss each classification one at a time
            in the order returned by the db.
            Parameters like max_batch_size are hard-coded.
            Prints status.
        """

        self.init_swap()

        # get classifications
        cursor = self.get_classifications()
        db_stats = swap.db.DB().get_stats()
        # n_classifications = self._n_classifications()

        # loop over classification cursor to process
        # classifications one at a time
        logger.info("Start: SWAP Processing %d classifications",
                    db_stats['first_classifications'])

        count = 0
        with progressbar.ProgressBar(
                max_value=db_stats['first_classifications']) as bar:
            # Loop over all classifications of the query
            # Note that the exact size of the query might be lower than
            # n_classifications if not all classifications are being queried
            for cl in cursor:
                # process classification in swap
                cl = Classification.generate(cl)
                self._delegate(cl)
                bar.update(count)
                count += 1

        if config.back_update:
            logger.info('back_update active: processing changes')
            self.swap.process_changes()
        logger.info('done')

    def _delegate(self, cl):
        """
        Passes classification to SWAP

        Purpose is to allow subclasses to override how SWAP receives
        classifications

        Parameters
        ----------
        cl : Classification
            Classification being delegated
        """
        self.swap.classify(cl)

    def init_swap(self):
        """
        Create a new SWAP instance, also passes SWAP the appropriate
        gold labels.

        Returns
        -------
        SWAP
            SWAP
        """
        logger.debug('Initializing SWAP')
        if self.swap is None:
            swap = SWAP()
        else:
            swap = self.swap

        golds = self.get_gold_labels()
        swap.set_gold_labels(golds)

        self.swap = swap
        return swap

    def get_gold_labels(self):
        """
        Get the set of gold labels being used for this run
        """
        return self.gold_getter.golds

    def get_classifications(self):
        """
        Get the cursor containing classifications from db

        Returns
        -------
        swap.db.Cursor
            Cursor with classifications
        """
        return db.getClassifications()

    def getSWAP(self):
        """
        Get the SWAP instance being used

        Returns
        -------
        SWAP
            SWAP
        """
        return self.swap

    def setSWAP(self, swap):
        """
        Set the SWAP object
        """
        self.swap = swap

    def reset(self):
        """
        Reset the gold getter and SWAP instances.

        Useful when running multiple subsequent instances of SWAP
        """
        self.swap = None
        self.gold_getter.reset()


class MetaDataControl(Control):
    """ Calls SWAP to process classifications for specific meta data splits
    """

    def __init__(self, p0, epsilon, meta_data, meta_lower, meta_upper):
        raise DeprecationWarning
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
