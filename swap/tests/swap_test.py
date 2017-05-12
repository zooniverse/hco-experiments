from swap.swap import SWAP
from swap.swap import ClValueError
from swap.swap import ClKeyError
from swap.swap import Classification

from pprint import pprint
import pytest


def test_set_gold():
    swap = SWAP(p0=2e-4, epsilon=1.0)
    labels = [0, 0, 0, 0, 1, 1, 1, 1]
    subjects = {}
    for i, l in enumerate(labels):
        subjects[i + 1] = l

    swap.setGoldLabels(subjects)

    export = swap.exportSubjectData()
    pprint(export)

    assert len(export) == 8
    assert export[1]['gold_label'] == 0
    assert export[8]['gold_label'] == 1


def test_get_gold():
    swap = SWAP(0.5, 0.5)
    labels = {0: 1, 1: 1, 2: 0, 3: 0}
    swap.setGoldLabels(labels)

    golds = swap.getGoldLabels()
    assert golds == labels


def test_export_nonempty():
    swap = SWAP(p0=2e-4, epsilon=1.0)

    cl1 = Classification('user_1', 'subject_1', 1, 1)
    cl2 = Classification('user_2', 'subject_1', 1, 1)

    swap.processOneClassification(cl1)
    swap.processOneClassification(cl2)

    export = swap.export()
    pprint(export)

    assert 'users' in export
    assert 'subjects' in export

    assert 'user_1' in export['users']
    assert 'user_2' in export['users']
    assert 'subject_1' in export['subjects']


def test_set_golds():
    swap = SWAP()
    golds = {1: 1, 2: 0, 3: 0}
    swap.setGoldLabels(golds)

    bureau = swap.getSubjectData()
    print(bureau)
    for id_, gold in golds.items():
        assert id_ in bureau
        assert bureau.getAgent(id_).gold == gold


def test_classification_without_gold():
    swap = SWAP(.5, .5)
    golds = {1: 1, 2: 0, 3: 0}
    swap.setGoldLabels(golds)

    cl = Classification('user', 1, 0)
    swap.processOneClassification(cl)

    bureau = swap.getUserData()
    agent = bureau.get('user')

    print(agent.export())
    assert len(agent.export()['score_1_history']) == 2
    assert len(agent.export()['score_0_history']) == 1


def test_doesnt_override_golds():
    swap = SWAP()
    golds = {1: 1, 2: 0, 3: 0}
    swap.setGoldLabels(golds)

    bureau = swap.getSubjectData()
    print(bureau)

    swap.processOneClassification(Classification(0, 2, 0, 1))
    print(bureau.getAgent(1))
    assert bureau.getAgent(2).gold == 0


def test_subject_gold_label_1():
    swap = SWAP(p0=2e-4, epsilon=1.0)
    swap.gold_from_cl = True

    swap.processOneClassification(Classification(1, 1, 0, 1))
    swap.processOneClassification(Classification(2, 1, 0, 0))

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == 1


def test_subject_gold_label_0():
    swap = SWAP(p0=2e-4, epsilon=1.0)
    swap.gold_from_cl = True

    swap.processOneClassification(Classification(1, 1, 0, 0))
    swap.processOneClassification(Classification(2, 1, 0, 1))

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == 0


def test_subject_no_gold_label():
    cl = Classification(1, 1, 1)

    swap = SWAP(p0=2e-4, epsilon=1.0)
    swap.processOneClassification(cl)

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == -1


@pytest.mark.skip()
def test_subject_update_perfect_classifier():
    cl = Classification('user_1', 'subject_1', 1, 1)

    swap = SWAP(p0=2e-4, epsilon=1.0)
    swap.processOneClassification(cl)

    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_1']['score'] == 1

    cl = Classification('user_1', 'subject_2', 0, 0)
    swap.processOneClassification(cl)

    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_2']['score'] == 0


@pytest.mark.skip()
def test_subject_update_obtuse_classifier():
    cl = Classification('user_1', 'subject_1', 0, 1)

    swap = SWAP(p0=2e-4, epsilon=0.0)
    swap.processOneClassification(cl)

    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_1']['score'] == 1

    cl = Classification('user_1', 'subject_2', 1, 0)

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_2']['score'] == 0


def my_volunteer_update(user, annotation, gold_label):
        user[gold_label]['tot'] += 1
        if gold_label == annotation:
                user[gold_label]['correct'] += 1
        user[gold_label]['p'] = \
            user[gold_label]['correct'] / float(user[gold_label]['tot'])
        return user


def my_subject_update(p0, user, annotation):

    if annotation == '1':
        S = p0*user['1']['p'] / (p0*user['1']['p'] + (1-user['0']['p'])*(1-p0))
    elif annotation == '0':
        S = p0*(1-user['1']['p']) / (p0*(1-user['1']['p']) + (user['0']['p'])*(1-p0))
    return S


def predict_subject_score(p0, user0, user1, annotation):
    if annotation == 1:
        return p0 * user1 / (p0 * user1 + (1 - user0) * (1 - p0))
    elif annotation == 0:
        return p0 * (1 - user1) / (p0 * (1 - user1) + user0 * (1 - p0))


def test_subject_update_apply_one_correct_classification():
    p0 = 0.2
    epsilon = 0.5
    annotation = 1
    gold_label = 1

    expected = predict_subject_score(p0, epsilon, epsilon, 1)
    assert expected == 1 / 5

    swap = SWAP(p0=p0, epsilon=epsilon)

    cl = Classification('user_1', 'subject_1', annotation, gold_label)

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint([export, expected])

    assert export['subject_1']['score'] == expected


def test_subject_update_apply_one_incorrect_classification():

    p0 = 0.2
    epsilon = 0.5
    annotation = 0
    gold_label = 1

    expected_subject_score = predict_subject_score(p0, epsilon, epsilon, 0)

    swap = SWAP(p0=p0, epsilon=epsilon)

    cl = Classification('user_1', 'subject_1', annotation, gold_label)

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint([export, expected_subject_score])

    assert export['subject_1']['score'] == expected_subject_score


class Test_Classification:
    def test_classification_gold_init(self):
        cl = Classification(0, 0, 0)

        print(cl)
        print(cl.gold_label)
        assert cl.isGold() is False
        assert cl.gold is False

    def test_init_type_errors(self):
        with pytest.raises(ClValueError):
            Classification(1, 1, '1')


def main():

    test_subject_update_perfect_classifier()
    test_subject_update_obtuse_classifier()

    test_subject_update_apply_one_correct_classification()
    test_subject_update_apply_one_incorrect_classification()


if __name__ == "__main__":
    main()
