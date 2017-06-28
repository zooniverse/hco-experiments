
import swap.db.classifications as db

import csv

import logging
logger = logging.getLogger(__name__)


class Score:
    """
    Stores information on each subject for export
    """

    def __init__(self, id_, gold, p):
        """
        Parameters
        ----------
        id_ : int
            Subject id
        gold : gold
            Gold label of subject
        p : float
            SWAP probability that the subject is real
        """
        self.id = id_
        self.gold = gold
        self.p = p

    def dict(self):
        return {'id': self.id, 'gold': self.gold, 'p': self.p}

    def __str__(self):
        return 'id: %d gold: %d p: %.3f' % (self.id, self.gold, self.p)

    def __repr__(self):
        return '{%s}' % self.__str__()


class ScoreExport:
    """
    Export SWAP scores

    Uses less space than pickling and saving the entire SWAP object.
    Used to generate plots like ROC curves.
    """

    def __init__(self, scores, new_golds=True):
        """
        Pararmeters
        -----------
        scores : {Score}
            Mapping of scores in export
        new_golds : bool
            Flag to indicate whether to fetch gold labels from database
            or to use the gold labels already in score objects
        """
        if new_golds:
            scores = self._init_golds(scores)
        self.scores = scores
        self._sorted_ids = sorted(scores, key=lambda id_: scores[id_].p)
        self.class_counts = self.counts(0)

    @staticmethod
    def from_csv(fname):
        data = {}

        with open(fname) as csvfile:
            reader = csv.reader(csvfile)
            logger.info('loading csv')

            for i, g, p in reader:
                i = int(i)
                g = int(g)
                p = float(p)
                data[i] = Score(i, g, p)

            logger.info('done')
        return ScoreExport(data, new_golds=False)

    @property
    def sorted_scores(self):
        for i in self._sorted_ids:
            yield self.scores[i]

    def _init_golds(self, scores):
        """
        Assign new gold labels to score objects

        Parameters
        ----------
        score : [Score]
            List of scores in export
        """
        golds = self.get_real_golds()
        for score in scores.values():
            if score.id in golds:
                score.gold = golds[score.id]
            else:
                score.gold = -1
        return scores

    @staticmethod
    def get_real_golds():
        """
        Fetch gold labels from database
        """
        logger.debug('Getting real gold labels from db')
        return db.getAllGolds()

    def counts(self, threshold):
        """
        Count how many subjects of each class are in the export

        Parameters
        ----------
        threshold : float
            Threshold for p values of Scores to consider
        """
        n = {-1: 0, 0: 0, 1: 0}
        for score in self.scores.values():
            if score.p >= threshold:
                n[score.gold] += 1
        return n

    def composition(self, threshold):
        """
        Measure percentage of each class in the export

        Parameters
        ----------
        threshold : float
            Threshold for p values of Scores to consider
        """
        n = self.counts(threshold)

        total = n[0] + n[1]
        if (total > 0):
            for i in n:
                n[i] = n[i] / total

        return n

    def purity(self, threshold):
        """
        Measure the purity of real objects in score export

        Parameters
        ----------
        threshold : float
            Threshold for p values of Scores to consider
        """
        return self._purity(self.counts(threshold))

    @staticmethod
    def _purity(counts):

        def total(counts):
            return counts[1] + counts[0]

        t = total(counts)
        if t > 0:
            return counts[1] / t

    def find_purity(self, desired_purity):
        """
        Determine the threshold for p needed to arrive at the
        desired purity.

        Parameters
        ----------
        desired_purity : float
        """

        logger.debug('Trying to find purity %.3f', desired_purity)

        counts = self.class_counts.copy()
        for score in self.sorted_scores:
            counts[score.gold] -= 1

            _purity = self._purity(counts)
            # print(_purity, score, counts)

            if _purity is not None and _purity > desired_purity:
                logger.info('found purity')
                logger.info('%f %s %s', _purity, str(score), str(counts))
                return score.p

        logger.info('Couldn\'t find purity above %f!', desired_purity)
        return 1.0

    def completeness(self, threshold):
        """
        Find the completeness at a desired purity

        Parameters
        ----------
        threshold : float
            Threshold for the desired purity
        """
        inside = 0
        total = 0

        for score in self.sorted_scores:
            if score.gold == 1:
                if score.p > threshold:
                    inside += 1
                total += 1

        return inside / total

    def completeness_at_purity(self, purity):
        """
        Find the completeness at a desired purity

        Parameters
        ----------
        threshold : float
            Threshold for the desired purity
        """
        p = self.find_purity(purity)
        if p is None:
            logger.error('Can\'t find purity > %f in score set!', purity)
            return 0

    def find_thresholds(self, fpr, mdr):
        totals = self.counts(0)

        # Calculate real retirement threshold
        count = 0
        real = 0
        for score in self.sorted_scores:
            if score.gold == 0:
                count += 1

            if 1 - count / totals[0] < fpr:
                real = score.p

        # Calculate bogus retirement threshold
        count = 0
        bogus = 0
        for score in reversed(list(self.sorted_scores)):
            if score.gold == 1:
                count += 1

            if 1 - count / totals[1] < mdr:
                bogus = score.p

        return bogus, real

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return iter(self.scores)

    def roc(self):
        """
        Generate iterator of information for a ROC curve
        """
        def func(score):
            return score.gold, score.p

        def isgold(score):
            return score.gold in [0, 1]

        scores = list(self.sorted_scores)
        return ScoreIterator(scores, func, isgold)

    def full(self):
        """
        Generate iterator of all information
        """
        def func(score):
            return (score.id, score.gold, score.p)
        return ScoreIterator(list(self.sorted_scores), func)

    def full_dict(self):
        d = {}
        for i in self.scores:
            score = self.scores[i]
            d[score.id] = score.dict()

        return d

    def dict(self):
        return self.scores.copy()


class ScoreIterator:
    """
    Custom iterator to process exported score data
    """

    def __init__(self, scores, func, cond=None):
        if type(scores) is dict:
            scores = list(scores.values())
        if type(scores) is not list:
            raise TypeError('scores type %s not valid!' % str(type(scores)))

        self.scores = scores
        self.func = func
        if cond is None:
            self.cond = lambda item: True
        else:
            self.cond = cond
        self.i = 0

    def next(self):
        if self.i >= len(self):
            raise StopIteration

        score = self.scores[self.i]
        self.i += 1

        if self.cond(score):
            obj = self.func(score)
            return obj
        else:
            return self.next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.scores)
