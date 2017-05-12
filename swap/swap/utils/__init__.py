
import swap.db.classifications as db


class Score:
    def __init__(self, id_, gold, p):
        self.id = id_
        self.gold = gold
        self.p = p


class ScoreExport:
    def __init__(self, swap):
        scores = {}
        golds = self.get_real_golds()
        for subject in swap.subjects:
            id_ = subject.id
            gold = golds[id_]
            score = subject.getScore()
            scores[id_] = Score(id_, gold, score)

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
        self.scores = scores
        self.func = func
        self.i = 0

    def next(self):
        obj = self.func(self.scores[self.i])
        self.i += 1
        return obj

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.scores)
