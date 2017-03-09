#!/usr/bin/env python
################################################################
# Script to test control functionality

import swap.mongo.db
from swap.control import Control

fields = {'user_id', 'classification_id', 'subject_id',
          'annotation', 'gold_label'}
db = swap.mongo.DB()


# def test_classifications_projection():
#     q = Query()
#     q.fields(['user_id', 'classification_id'])
#     raw = db.classifications.aggregate(q.build())

#     item = raw.next()

#     assert 'user_id' in item
#     assert 'classification_id' in item
#     assert 'subject_id' not in item


# def test_classifications_limit():
#     q = Query()
#     q.fields(fields).limit(5)
#     raw = db.classifications.aggregate(q.build())

#     assert len(list(raw)) == 5


# def test_users():
#     control = swap.Server(.5, .5)
#     users = control.getClassificationsByUser()

#     pprint(list(users))


def test_get_one_classification():
    """ Get the first classification
    """
    control = Control(0.5, 0.5)

    classification_cursor = control.classifications.find()
    n_class = classification_cursor.count()
    current_classification = classification_cursor.next()

    assert n_class > 0
    assert type(current_classification) == dict
    assert len(current_classification) > 0
