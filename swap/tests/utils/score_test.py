################################################################

from swap.utils.scores import ScoreExport, Score, ScoreIterator
import swap.db.classifications as dbcl
from swap.agents.subject import Subject

from unittest.mock import MagicMock, patch


class TestScoreExport:

    @patch.object(dbcl, 'getAllGolds')
    def test_init(self, mock):
        golds = {1: 0, 2: 0, 3: 1, 4: 1}
        scores = {}
        for i, g in golds.items():
            scores[i] = Score(i, g, i / 10)

        se = ScoreExport(scores, False)
        print(se.scores)

        assert len(se.scores) == 4
        for score in se.scores.values():
            assert score.gold == golds[score.id]
            assert score.p == score.id / 10

    def test_counts(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.counts(0) == {-1: 1, 0: 2, 1: 3}

    def test_composition(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.composition(0) == {-1: 1 / 6, 0: 1 / 3, 1: 1 / 2}

    def test_purity(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert se.purity(0) == .5

    def test_builtins(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(se.scores)

        assert len(se) == 6
        iter(se)

    def test_roc(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(list(se.roc()))

        for i, item in enumerate(se.roc()):
            g, p = item
            assert g == golds[i + 1]
            assert p == 0

    def test_roc_notgold(self):
        golds = {0: -1, 1: 0, 2: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)
        print(list(se.roc()))

        assert len(list(se.roc())) == 2

    def test_roc_labels(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        se = ScoreExport(scores, False)

        roc = list(se.roc(labels=(2, 3, 4)))
        print(roc)

    def test_find_purity(self):
        golds = [0, 0, 0, 0, 1, 1, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)

        p = se.find_purity(0.99)
        print(p)
        assert p == 0.3

    def test_find_purity_2(self):
        golds = [0, 1, 0, 1, 0, 1, 0, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)

        p = se.find_purity(0.99)
        print(p)
        assert p == 0.6

    def test_completeness(self):
        golds = [1, 1, 0, 0, 1, 1]
        scores = dict([(i, Score(i, g, i / 10))
                       for i, g in enumerate(golds)])
        se = ScoreExport(scores, False)
        print(se.find_purity(0.8))
        c = se.completeness(0.8)

        assert c == 0.5


class TestScoreIterator:
    def test_(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])

        si = ScoreIterator(scores, lambda score: score)
        for score in si:
            i = score.id
            id_ = scores[i].id
            gold = scores[i].gold
            p = scores[i].p

            assert score.id == id_
            assert score.gold == gold
            assert score.p == p
