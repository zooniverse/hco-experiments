
# from swap.swap import SWAP
# from swap.utils.classification import ClValueError
# from swap.swap import ClKeyError
# from swap.utils import Classification

# from pprint import pprint
# import pytest

# p0 = 0.12
# epsilon = 0.5


# class TestSwapCalculations:

#     @pytest.mark.skip()
#     def test_subject_update_perfect_classifier():
#         cl = Classification('user_1', 'subject_1', 1, 1)

#         swap = SWAP(p0=2e-4, epsilon=1.0)
#         swap.processOneClassification(cl)

#         export = swap.exportSubjectData()
#         pprint(export)

#         assert export['subject_1']['score'] == 1

#         cl = Classification('user_1', 'subject_2', 0, 0)
#         swap.processOneClassification(cl)

#         export = swap.exportSubjectData()
#         pprint(export)

#         assert export['subject_2']['score'] == 0

#     @pytest.mark.skip()
#     def test_subject_update_obtuse_classifier():
#         cl = Classification('user_1', 'subject_1', 0, 1)

#         swap = SWAP(p0=2e-4, epsilon=0.0)
#         swap.processOneClassification(cl)

#         export = swap.exportSubjectData()
#         pprint(export)

#         assert export['subject_1']['score'] == 1

#         cl = Classification('user_1', 'subject_2', 1, 0)

#         swap.processOneClassification(cl)
#         export = swap.exportSubjectData()
#         pprint(export)

#         assert export['subject_2']['score'] == 0

#     def test_subject_update_apply_one_correct_classification():
#         p0 = 0.2
#         epsilon = 0.5
#         annotation = 1
#         gold_label = 1

#         expected = predict_subject_score(p0, epsilon, epsilon, 1)
#         assert expected == 1 / 5

#         swap = SWAP(p0=p0, epsilon=epsilon)

#         cl = Classification('user_1', 'subject_1', annotation, gold_label)

#         swap.processOneClassification(cl)
#         export = swap.exportSubjectData()
#         pprint([export, expected])

#         assert export['subject_1']['score'] == expected

#     def test_subject_update_apply_one_incorrect_classification(self):

#         p0 = 0.2
#         epsilon = 0.5
#         annotation = 0
#         gold_label = 1

#         expected_subject_score = predict_subject_score(p0, epsilon, epsilon, 0)

#         swap = SWAP(p0=p0, epsilon=epsilon)

#         cl = Classification('user_1', 'subject_1', annotation, gold_label)

#         swap.processOneClassification(cl)
#         export = swap.exportSubjectData()
#         pprint([export, expected_subject_score])

#         assert export['subject_1']['score'] == expected_subject_score


# def my_volunteer_update(user, annotation, gold_label):
#         user[gold_label]['tot'] += 1
#         if gold_label == annotation:
#                 user[gold_label]['correct'] += 1
#         user[gold_label]['p'] = \
#             user[gold_label]['correct'] / float(user[gold_label]['tot'])
#         return user


# def my_subject_update(p0, user, annotation):

#     if annotation == '1':
#         S = p0*user['1']['p'] / (p0*user['1']['p'] + (1-user['0']['p'])*(1-p0))
#     elif annotation == '0':
#         S = p0*(1-user['1']['p']) / (p0*(1-user['1']['p']) + (user['0']['p'])*(1-p0))
#     return S


# def predict_subject_score(p0, user0, user1, annotation):
#     if annotation == 1:
#         return p0 * user1 / (p0 * user1 + (1 - user0) * (1 - p0))
#     elif annotation == 0:
#         return p0 * (1 - user1) / (p0 * (1 - user1) + user0 * (1 - p0))
