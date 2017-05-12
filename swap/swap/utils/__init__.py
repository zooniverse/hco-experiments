
import swap.db.classifications as db


class Score:
    def __init__(self, id_, gold, p):
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
    def __init__(self, swap):
        self.scores = self._init_scores(swap)

    def _init_scores(self, swap):
        scores = {}
        golds = self.get_real_golds()
        for subject in swap.subjects:
            id_ = subject.id
            gold = golds[id_]
            score = subject.score
            scores[id_] = Score(id_, gold, score)
        return scores

    def get_real_golds(self):
        return db.getAllGolds()

    def purity(self, threshold):
        n = {-1: 0, 0: 0, 1: 0}
        for score in self.scores.values():
            if score.p >= threshold:
                n[score.gold] += 1

        return n

    def __len__(self):
        return len(self.scores)

    def __iter__(self):
        return self.scores.values()

    def roc(self):
        return ScoreIterator(self.scores.values(),
                             lambda score: (score.gold, score.p))


class ScoreIterator:
    def __init__(self, scores, func):
        if type(scores) is dict:
            scores = list(scores.values())
        if type(scores) is not list:
            raise TypeError

        self.scores = scores
        self.func = func
        self.i = 0

    def next(self):
        if self.i >= len(self):
            raise StopIteration
        obj = self.func(self.scores[self.i])
        self.i += 1
        return obj

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.scores)
