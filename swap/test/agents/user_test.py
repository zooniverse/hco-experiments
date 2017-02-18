################################################################
# Test functions for agent class

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
uid = cl['user_id']
epsilon = .5


class TestUser:
    def test_init(self):
        u = User(uid, epsilon)

        assert type(u.annotations) is Tracker
        assert type(u.gold_labels) is Tracker

        assert type(u.trackers) is Labeled_Trackers
