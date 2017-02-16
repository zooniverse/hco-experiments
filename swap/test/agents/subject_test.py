################################################################
# Test functions for agent class

from swap.agents.subject import Subject

from swap.agents.tracker import *

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


class TestSubject:
    def test_init(self):
        s = Subject(cl['subject_id'], .5)

        assert s.annotations is Tracker
        assert s.user_scores is Tracker
        assert s.tracker is Tracker
