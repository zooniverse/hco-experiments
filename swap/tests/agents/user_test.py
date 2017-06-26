################################################################
# Test functions for user agent class

import swap.agents.subject as _subject
import swap.agents.user as _user
from swap.agents.bureau import Bureau
from swap.utils.classification import Classification

import pytest

Subject = _subject.Subject
User = _user.User

# Sample classification
# cl = Classification.generate({
#     'user_name': 'HTMAMR38',
#     'metadata': {'mag_err': 0.1, 'mag': 20.666},
#     'gold_label': 0,
#     'diff': '1172057211575001100_57535.517_76128180_554_diff.jpeg',
#     'object_id': '1172057211575001100',
#     'classification_id': 13216944,
#     'annotation': 1,
#     'subject_id': 2149031,
#     'machine_score': 0.960535,
#     'user_id': 1497743})
# uid = 0
# epsilon = .5


class TestUser:
    def test_init(self):
        u = User(1)

        assert u.id == 1
        assert type(u.ledger) is _user.Ledger

    def test_score_property(self):
        u = User(1)
        u.ledger.recalculate()

        assert u.score == (.5, .5)

    def test_classify(self):
        u = User(11)
        s = Subject(12)
        s.set_gold_label(0, None)

        cl = Classification(11, 12, 1)
        u.classify(cl, s)

        print(u.ledger.transactions)
        t = u.ledger.get(12)
        assert t.annotation == 1
        assert t.change == 0
        assert t.id == 12

    def test_classify_rejects_wrong_classification(self):
        u = User(1)
        cl = Classification(2, 0, 0)
        with pytest.raises(ValueError):
            u.classify(cl, None)

    # @patch.object(Tracker, 'add')
    # def test_addcl_updates_annotation_gold_labels(self, mock):
    #     u = User(uid, epsilon)
    #     u.annotations.add = MagicMock()
    #     u.gold_labels.add = MagicMock()
    #     u.trackers.trackers[0].add = MagicMock()

    #     u.addClassification(cl, cl.gold)
    #     u.annotations.add.assert_called_once_with(1)
    #     u.gold_labels.add.assert_called_once_with(0)
    #     u.trackers.trackers[0].add.assert_called_once_with(1)

    # def test_score_all_correct(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 1),
    #         (1, 1),
    #         (1, 1),
    #         (1, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     assert u.getScore(1) == 5 / 6

    # def test_score_half_correct(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 1),
    #         (1, 1),
    #         (1, 0),
    #         (1, 0)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     assert u.getScore(1) == 3 / 6

    # def test_score_0_correct(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 0),
    #         (1, 0)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     assert u.getScore(1) == 1 / 6

    # def test_export_score0(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 1),
    #         (1, 1),
    #         (0, 0),
    #         (0, 0),
    #         (0, 1),
    #         (0, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     export = u.export()
    #     pprint(export)
    #     assert export['score_0'] == .5

    # def test_export_score1(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 1),
    #         (1, 1),
    #         (0, 0),
    #         (0, 0),
    #         (0, 1),
    #         (0, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     export = u.export()
    #     pprint(export)
    #     assert export['score_1'] == .5

    # def test_export_gold_labels(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 1),
    #         (1, 1),
    #         (0, 0),
    #         (0, 0),
    #         (0, 1),
    #         (0, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     export = u.export()
    #     pprint(export)
    #     assert export['gold_labels'] == [1, 1, 1, 1, 0, 0, 0, 0]

    # def test_export_score0_history(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 1),
    #         (1, 1),
    #         (0, 0),
    #         (0, 0),
    #         (0, 1),
    #         (0, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     export = u.export()
    #     pprint(export)
    #     assert export['score_0_history'] == [.5, 2/3, 3/4, 3/5, 3/6]

    # def test_export_score1_history(self):
    #     u = User(uid, epsilon)
    #     data = [
    #         (1, 0),
    #         (1, 0),
    #         (1, 1),
    #         (1, 1),
    #         (0, 0),
    #         (0, 0),
    #         (0, 1),
    #         (0, 1)
    #     ]

    #     for g, a in data:
    #         u.addClassification(Classification(0, 0, a), g)

    #     export = u.export()
    #     pprint(export)
    #     assert export['score_1_history'] == [.5, 1 / 3, 1 / 4, 2 / 5, 3 / 6]

    def test_bureau_stats(self):
        b = Bureau(User)
        b.add(User(0))
        b.add(User(1))
        b.add(User(2))

        for u in b:
            u.ledger.recalculate()

        s = b.stats()
        assert 0 in s.stats
        assert 1 in s.stats
        assert len(s.stats) == 2
