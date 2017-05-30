
import swap.db.classifications as db

import csv


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
        self.sorted_scores = sorted(scores, key=lambda id_: scores[id_].p)
        self.class_counts = self.counts(0)

    @staticmethod
    def from_csv(fname):
        data = {}
        with open(fname) as csvfile:
            reader = csv.reader(csvfile)
            print('loading csv')
            for i, g, p in reader:
                i = int(i)
                g = int(g)
                p = float(p)
                data[i] = Score(i, g, p)
                # print(i, g, p)
            print('done')

        return ScoreExport(data, new_golds=False)

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
            score.gold = golds[score.id]
        return scores

    def get_real_golds(self):
        """
        Fetch gold labels from database
        """
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

        total = sum(n.values())
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
        return self.composition(threshold)[1]

    def find_purity(self, desired_purity):
        """
        Determine the threshold for p needed to arrive at the
        desired purity.

        Parameters
        ----------
        desired_purity : float
        """
        def purity(counts):
            total = sum(counts.values())
            if total > 0:
                return counts[1] / sum(counts.values())

        counts = self.class_counts.copy()
        for id_ in self.sorted_scores:

            score = self.scores[id_]
            counts[score.gold] -= 1

            _purity = purity(counts)
            print(score, _purity, counts)

            if _purity is not None and _purity > desired_purity:
                return score.p

    def completeness(self, threshold):
        """
        Find the completeness at a desired purity

        Parameters
        ----------
        threshold : float
            Threshold for the desired purity
        """
        p = self.find_purity(threshold)
        if p is None:
            raise Exception(
                'Can\'t find purity > %d in score set!' % threshold)

        print(p, threshold)
        return self.counts(p)[1] / self.class_counts[1]

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return iter(self.scores)

    def roc(self, labels=None):
        """
        Generate iterator of information for a ROC curve
        """
        def func(score):
            return score.gold, score.p

        def isgold(score):
            return score.gold in [0, 1]

        scores = self.scores

        if labels is None:
            return ScoreIterator(scores, func, isgold)
        else:
            def cond(score):
                return isgold(score) and score.id in labels
            return ScoreIterator(scores, func, cond)

    def full(self):
        """
        Generate iterator of all information
        """
        def func(score):
            return (score.id, score.gold, score.p)
        return ScoreIterator(self.scores, func)

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
