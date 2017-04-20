#!/usr/bin/env python
################################################################
# Script to test control functionality

from swap.mongo.db import DB
from swap.control import Control
from unittest.mock import MagicMock
import pytest

fields = {'user_id', 'classification_id', 'subject_id',
          'annotation', 'gold_label'}


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


@pytest.mark.skip(reason='Takes too long')
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


def test_with_train_split():
    db = DB()
    old = db.getRandomGoldSample
    mock = MagicMock(return_value=[])
    db.getRandomGoldSample = mock

    Control(.5, .5, train_size=100)

    mock.assert_called_with(100)

    db.getRandomGoldSample = old


def test_without_train_split():
    db = DB()
    old = db.getAllGolds
    mock = MagicMock(return_value=[])
    db.getAllGolds = mock

    Control(.5, .5)

    mock.assert_called_with()

    db.getAllGolds = old
