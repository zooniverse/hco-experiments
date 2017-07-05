from swap import SWAP
from swap.utils.classification import Classification
from swap.agents.bureau import Bureau
from swap.agents.user import User
from swap.agents.subject import Subject
from swap.agents.agent import Stats

from unittest.mock import MagicMock

import pytest

# pylint: disable=R0201


class TestSwap:

    def test_init(self):
        swap = SWAP()

        assert type(swap.users) is Bureau
        assert type(swap.subjects) is Bureau
        assert swap.users.agent_type is User
        assert swap.subjects.agent_type is Subject

    @pytest.mark.skip()
    def test_classify_user(self):
        swap = SWAP()
        u = User(1)
        s = Subject(2)
        s._gold = 1

        u.classify = MagicMock()
        s.classify = MagicMock()

        swap.users.add(u)
        swap.subjects.add(s)

        cl = Classification(1, 2, 0, 0)
        swap.classify(cl, subject=False, user=True)

        u.classify.assert_called_with(cl, s)
        s.classify.assert_not_called()

    @pytest.mark.skip()
    def test_classify_subject(self):
        swap = SWAP()
        u = User(1)
        s = Subject(2)
        s._gold = 1

        u.classify = MagicMock()
        s.classify = MagicMock()

        swap.users.add(u)
        swap.subjects.add(s)

        cl = Classification(1, 2, 0, 0)
        swap.classify(cl, subject=True, user=False)

        u.classify.assert_not_called()
        s.classify.assert_called_with(cl, u)

    def test_set_gold(self):
        swap = SWAP()
        labels = {0: 1, 1: 1, 2: 0, 3: 0}
        swap.set_gold_labels(labels)

        b = swap.subjects
        for i, g in labels.items():
            assert i in b
            assert b.get(i).gold == g

    def test_set_gold_negates(self):
        swap = SWAP()
        subject = Subject(0)
        subject._gold = 1
        swap.subjects.add(subject)

        swap.set_gold_labels({})

        print(type(subject.gold))
        print(subject.gold)
        assert subject.gold == -1

    def test_get_gold(self):
        swap = SWAP()
        labels = {0: 1, 1: 1, 2: 0, 3: 0}
        swap.set_gold_labels(labels)

        assert swap.golds == labels

    def test_stats_empty(self):
        swap = SWAP()
        swap.stats

    def test_stats(self):
        swap = SWAP()
        golds = {0: 1, 1: 1, 2: 0, 3: 0}
        swap.set_gold_labels(golds)

        for x in range(10):
            for y in range(10):
                swap.classify(Classification(x, y, 0))
        swap.process_changes()

        stats = swap.stats
        print(stats)
        assert type(stats) is Stats

    def test_manifest(self):
        swap = SWAP()
        golds = {0: 1, 1: 1, 2: 0, 3: 0}
        swap.set_gold_labels(golds)

        for x in range(10):
            for y in range(10):
                swap.classify(Classification(x, y, 0))
        swap.process_changes()

        print(swap.manifest())


    # def test_export_nonempty(self):
    #     swap = SWAP(p0=2e-4, epsilon=1.0)

    #     cl1 = Classification('user_1', 'subject_1', 1, 1)
    #     cl2 = Classification('user_2', 'subject_1', 1, 1)

    #     swap.processOneClassification(cl1)
    #     swap.processOneClassification(cl2)

    #     export = swap.export()
    #     pprint(export)

    #     assert 'users' in export
    #     assert 'subjects' in export

    #     assert 'user_1' in export['users']
    #     assert 'user_2' in export['users']
    #     assert 'subject_1' in export['subjects']

    # def test_classification_without_gold(self):
    #     swap = SWAP(.5, .5)
    #     golds = {1: 1, 2: 0, 3: 0}
    #     swap.setGoldLabels(golds)

    #     cl = Classification('user', 1, 0)
    #     swap.processOneClassification(cl)

    #     bureau = swap.getUserData()
    #     agent = bureau.get('user')

    #     print(agent.export())
    #     assert len(agent.export()['score_1_history']) == 2
    #     assert len(agent.export()['score_0_history']) == 1

    def test_doesnt_override_golds(self):
        swap = SWAP()
        golds = {1: 1, 2: 0, 3: 0}
        swap.set_gold_labels(golds)

        bureau = swap.subjects
        print(bureau)

        cl = Classification(0, 2, 0)
        cl.gold = 1
        swap.classify(cl)
        swap.process_changes()
        print(bureau.get(1))
        assert bureau.get(2).gold == 0

    # def test_subject_gold_label_1(self):
    #     swap = SWAP(p0=2e-4, epsilon=1.0)
    #     swap.gold_from_cl = True

    #     swap.processOneClassification(Classification(1, 1, 0, 1))
    #     swap.processOneClassification(Classification(2, 1, 0, 0))

    #     export = swap.exportSubjectData()
    #     pprint(export)
    #     assert export[1]['gold_label'] == 1

    # def test_subject_gold_label_0(self):
    #     swap = SWAP(p0=2e-4, epsilon=1.0)
    #     swap.gold_from_cl = True

    #     swap.processOneClassification(Classification(1, 1, 0, 0))
    #     swap.processOneClassification(Classification(2, 1, 0, 1))

    #     export = swap.exportSubjectData()
    #     pprint(export)
    #     assert export[1]['gold_label'] == 0

    # def test_subject_no_gold_label(self):
    #     cl = Classification(1, 1, 1)

    #     swap = SWAP(p0=2e-4, epsilon=1.0)
    #     swap.processOneClassification(cl)

    #     export = swap.exportSubjectData()
    #     pprint(export)
    #     assert export[1]['gold_label'] == -1
