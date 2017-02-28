################################################################
# Test functions for agent class

from swap.agents.subject import Subject
from swap.agents.user import User
from swap.agents.tracker import *

from unittest.mock import patch, MagicMock, call, Mock

# Sample classification
cl = {
    'user_name': 'HTMAMR38',
    'metadata': {'mag_err': '0.1', 'mag': '20.666'},
    'gold_label': '0',
    'diff': '1172057211575001100_57535.517_76128180_554_diff.jpeg',
    'object_id': '1172057211575001100',
    'classification_id': '13216944',
    'annotation': '1',
    'subject_id': '2149031',
    'machine_score': '0.960535',
    'user_id': '1497743'
    }
sid = cl['subject_id']
p0 = .5


class TestSubject:
    def test_init(self):
        s = Subject(sid, p0)

        assert type(s.annotations) is Tracker
        assert type(s.user_scores) is Tracker
        assert type(s.tracker) is Tracker

    @patch.object(Tracker, 'add')
    def test_addcl_updates_annotation_user_score(self, mock):
        s = Subject(sid, p0)
        s.calculateScore = MagicMock(return_value=100)

        user = User('', .5)
        user.trackers.get(0)._current = .5
        user.trackers.get(1)._current = .5

        s.addClassification(cl, user)

        calls = [call(1), call(.5), call(100)]
        mock.assert_has_calls(calls)

    @patch.object(Subject, 'calculateScore')
    def test_addcl_calls_calculateScore(self, mock):
        s = Subject(sid, 2)

        user = User('', 100)
        user.trackers.get(0)._current = 3
        user.trackers.get(1)._current = 4

        s.addClassification(cl, user)

        mock.assert_called_once_with(1, 3, 4, 2)

    def test_getLabel_1(self):
        s = Subject(sid, 2)
        s.getScore = MagicMock(return_value=.51)

        assert s.getLabel() == 1

    def test_getLabel_0(self):
        s = Subject(sid, 2)
        s.getScore = MagicMock(return_value=.5)

        assert s.getLabel() == 0

    # Potential outline for unit test to calculate score
    def test_calculateScore(self):
        s = Subject(sid, 2)

        annotation = 1
        u_score_0 = 0
        u_score_1 = 0
        s_score = 0
        score = s.calculateScore(annotation, u_score_0, u_score_1, s_score)

        assert score == 0
