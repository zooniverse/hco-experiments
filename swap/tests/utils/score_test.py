################################################################

from swap.utils import ScoreExport, Score, ScoreIterator
import swap.db.classifications as dbcl
from swap.agents.subject import Subject

from unittest.mock import MagicMock, patch


class TestScoreExport:

    @patch.object(dbcl, 'getAllGolds')
    def test_init(self, mock):
        golds = {1: 0, 2: 0, 3: 1, 4: 1}
        mock.return_value = golds

        swap = MagicMock()
        swap.subjects = []
        for i in range(1, 5):
            s = Subject(i)
            s.ledger._score = i / 10
            s.ledger.stale = False
            swap.subjects.append(s)

        se = ScoreExport(swap)
        print(se.scores)

        assert len(se.scores) == 4
        for score in se.scores.values():
            assert score.gold == golds[score.id]
            assert score.p == score.id / 10

    def test_counts(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(se.scores)

        assert se.counts(0) == {-1: 1, 0: 2, 1: 3}

    def test_composition(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(se.scores)

        assert se.composition(0) == {-1: 1 / 6, 0: 1 / 3, 1: 1 / 2}

    def test_purity(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(se.scores)

        assert se.purity(0) == .5

    def test_builtins(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(se.scores)

        assert len(se) == 6
        iter(se)

    def test_roc(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(list(se.roc()))

        for i, item in enumerate(se.roc()):
            g, p = item
            assert g == golds[i + 1]
            assert p == 0

    def test_roc_labels(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)

        roc = list(se.roc(labels=(2, 3, 4)))
        print(roc)


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
