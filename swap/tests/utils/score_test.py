################################################################

from swap.utils import ScoreExport, Score, ScoreIterator
import swap.db.classifications as dbcl
from swap.agents import Subject

from unittest.mock import MagicMock


class TestScoreExport:
    def test_init(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1}
        dbcl.getAllGolds = MagicMock(return_value=golds)
        swap = MagicMock()
        swap.subjects = []
        for i in range(1, 5):
            s = Subject(i, .12)
            s.tracker.add(i / 10)
            swap.subjects.append(s)

        se = ScoreExport(swap)
        print(se.scores)

        assert len(se.scores) == 4
        for score in se.scores.values():
            assert score.gold == golds[score.id]
            assert score.p == score.id / 10

    def test_purity(self):
        golds = {1: 0, 2: 0, 3: 1, 4: 1, 5: -1, 6: 1}
        scores = dict([(i, Score(i, g, 0)) for i, g in golds.items()])
        ScoreExport._init_scores = MagicMock(return_value=scores)

        se = ScoreExport(None)
        print(se.scores)

        assert se.purity(0) == {-1: 1, 0: 2, 1: 3}


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
