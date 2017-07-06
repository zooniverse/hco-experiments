################################################################
# Test functions for agent class

import swap.agents.subject as _subject
import swap.agents.user as _user
from swap.agents.bureau import Bureau
from swap.agents.ledger import Ledger
from swap.utils.classification import Classification

import pytest
from unittest.mock import MagicMock, patch

Subject = _subject.Subject
User = _user.User

# pylint: disable=R0201


class TestSubject:
    def test_init(self):
        s = Subject(1)

        assert s.id == 1
        assert type(s.ledger) is _subject.Ledger
        assert s.gold == -1

    def test_gold_property(self):
        s = Subject(1)

        with pytest.raises(AttributeError):
            s.gold = 1

    def test_isgold_true(self):
        s = Subject(1, 0)
        assert s.isgold()

        s = Subject(1, 1)
        assert s.isgold()

    def test_isgold_false(self):
        s = Subject(1)
        assert not s.isgold()

    def test_score_property(self):
        s = Subject(1)
        s.ledger.recalculate()
        assert s.score == 0.12

    def test_classify(self):
        s = Subject(12)
        cl = Classification(11, 12, 1)

        u = User(11)
        u.ledger.recalculate()
        s.classify(cl, u)

        t = s.ledger.get(11)
        assert t.annotation == 1
        assert t.id == 11
        print(t)

        s.ledger.recalculate()
        _ = s.score

    def test_classify_rejects_wrong_classification(self):
        s = Subject(1)
        cl = Classification(0, 2, 0)
        with pytest.raises(ValueError):
            s.classify(cl, None)

    # @patch.object(Tracker, 'add')
    # def test_addcl_updates_annotation_user_score(self, mock):
    #     s = Subject(sid, p0)
    #     s.calculateScore = MagicMock(return_value=100)

    #     user = User('', .5)
    #     user.trackers.get(0)._current = .5
    #     user.trackers.get(1)._current = .5

    #     s.addClassification(cl, user)

    #     calls = [call(1), call((.5, .5)), call(100)]
    #     mock.assert_has_calls(calls)

    # @patch.object(Subject, 'calculateScore')
    # def test_addcl_calls_calculateScore(self, mock):
    #     s = Subject(sid, 2)

    #     user = User('', 100)
    #     user.trackers.get(0)._current = 3
    #     user.trackers.get(1)._current = 4

    #     s.addClassification(cl, user)

    #     mock.assert_called_once_with(1, 3, 4, 2)

    # def test_getLabel_1(self):
    #     s = Subject(sid, 2)
    #     s.score = .51

    #     assert s.label == 1

    # def test_getLabel_0(self):
    #     s = Subject(sid, 2)
    #     s.score = .5

    #     assert s.label == 0

    # Potential outline for unit test to calculate score
    # def test_calculateScore(self):
    #     s = Subject(sid, 2)

    #     annotation = 1
    #     u_score_0 = 0
    #     u_score_1 = 0
    #     s_score = 0
    #     score = s.calculateScore(annotation, u_score_0, u_score_1, s_score)

    #     assert score == 0

    @patch.object(Ledger, 'notify_agents', MagicMock())
    def test_set_gold_label(self):
        s = Subject(1)
        assert s.gold == -1

        s.set_gold_label(1, 15, 16)
        assert s.gold == 1

    @patch.object(Ledger, 'notify_agents', return_value=MagicMock())
    def test_set_gold_label_notify_ledger(self, mock):
        s = Subject(1)
        assert s.gold == -1

        s.set_gold_label(1, 15, 16)
        mock.assert_called_once_with(15, 16)

    @patch.object(Ledger, 'notify_agents', return_value=MagicMock())
    def test_set_gold_label_no_notify(self, mock):
        s = Subject(1)
        assert s.gold == -1

        s._gold = 1
        s.set_gold_label(1, 15, 16)
        mock.assert_not_called()

    # ---------EXPORT TEST------------------------------

    # @patch.object(User, 'getScore', side_effect=[.5, .5, .5])
    # def test_export_contents(self, mock):
    #     s = Subject(sid, .5)
    #     u = User(0, .5)

    #     cl = Classification(0, sid, 0)
    #     s.addClassification(cl, u)

    #     export = s.export()
    #     assert 'user_scores' in export
    #     assert 'score' in export
    #     assert 'history' in export

    # @patch.object(User, 'getScore', side_effect=[.5, .5, .5])
    # def test_export_contents_match(self, mock):
    #     s = Subject(sid, .5)
    #     u = User(0, .5)

    #     cl = Classification(0, sid, 0)
    #     s.addClassification(cl, u)

    #     export = s.export()
    #     assert export['user_scores'] == [(.5, .5)]
    #     assert export['score'] == .5
    #     assert export['history'] == [.5, .5]
