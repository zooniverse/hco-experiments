from swap.swap import SWAP
import pytest
from pprint import pprint


def test_export_nonempty():
    swap = SWAP(p0=2e-4, epsilon=1.0)

    cl1 = {
        'user_name': 'user_1',
        'subject_id': 'subject_1',
        'annotation': 1,
        'gold_label': 1
    }

    cl2 = {
        'user_name': 'user_2',
        'subject_id': 'subject_1',
        'annotation': 1,
        'gold_label': 1
    }

    swap.processOneClassification(cl1)
    swap.processOneClassification(cl2)

    export = swap.export()
    pprint(export)

    assert 'users' in export
    assert 'subjects' in export

    assert 'user_1' in export['users']
    assert 'user_2' in export['users']
    assert 'subject_1' in export['subjects']


def test_subject_gold_label_1():
    def make_cl(u, s, a, g):
        return {
            'user_name': u,
            'subject_id': s,
            'annotation': a,
            'gold_label': g
        }

    swap = SWAP(p0=2e-4, epsilon=1.0)

    swap.processOneClassification(make_cl(1, 1, 0, 1))
    swap.processOneClassification(make_cl(2, 1, 0, 0))

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == 1


def test_subject_gold_label_0():
    def make_cl(u, s, a, g):
        return {
            'user_name': u,
            'subject_id': s,
            'annotation': a,
            'gold_label': g
        }

    swap = SWAP(p0=2e-4, epsilon=1.0)

    swap.processOneClassification(make_cl(1, 1, 0, 0))
    swap.processOneClassification(make_cl(2, 1, 0, 1))

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == 0


def test_subject_no_gold_label():
    cl = {
        'user_name': 1,
        'subject_id': 1,
        'annotation': 1
    }

    swap = SWAP(p0=2e-4, epsilon=1.0)

    swap.processOneClassification(cl)

    export = swap.exportSubjectData()
    pprint(export)
    assert export[1]['gold_label'] == -1


def test_subject_update_perfect_classifier():

    swap = SWAP(p0=2e-4, epsilon=1.0)

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_1',
        'annotation': 1,
        'gold_label': 1
    }

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_1']['score'] == 1

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_2',
        'annotation': 0,
        'gold_label': 0
    }

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_2']['score'] == 0


def test_subject_update_obtuse_classifier():

    swap = SWAP(p0=2e-4, epsilon=0.0)

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_1',
        'annotation': 0,
        'gold_label': 1
    }

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint(export)

    assert export['subject_1']['score'] == 1

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_2',
        'annotation': 1,
        'gold_label': 0
    }

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

    expected_subject_score = predict_subject_score(p0, epsilon, 1, 1)
    assert expected_subject_score == 1 / 3

    swap = SWAP(p0=p0, epsilon=epsilon)

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_1',
        'annotation': annotation,
        'gold_label': gold_label
    }

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint([export, expected_subject_score])

    assert export['subject_1']['score'] == expected_subject_score


def test_subject_update_apply_one_incorrect_classification():

    p0 = 0.2
    epsilon = 0.5
    annotation = 0
    gold_label = 1

    expected_subject_score = predict_subject_score(p0, epsilon, 0, 0)

    swap = SWAP(p0=p0, epsilon=epsilon)

    cl = {
        'user_name': 'user_1',
        'subject_id': 'subject_1',
        'annotation': annotation,
        'gold_label': gold_label
    }

    swap.processOneClassification(cl)
    export = swap.exportSubjectData()
    pprint([export, expected_subject_score])

    assert export['subject_1']['score'] == expected_subject_score

def main():

    test_subject_update_perfect_classifier()
    test_subject_update_obtuse_classifier()

    test_subject_update_apply_one_correct_classification()
    test_subject_update_apply_one_incorrect_classification()


if __name__ == "__main__":
    main()
