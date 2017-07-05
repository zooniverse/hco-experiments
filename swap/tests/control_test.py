#!/usr/bin/env python
################################################################
# Script to test control functionality

from swap.db.classifications import Classifications
from swap.db.golds import Golds
from swap.db import DB
from swap.control import Control
from swap.utils.golds import GoldGetter

from unittest.mock import MagicMock, patch
import pytest

# pylint: disable=R0201

fields = {'user_id', 'classification_id', 'subject_id',
          'annotation', 'gold_label'}


def db_cl():
    return DB().classifications


class TestControl:

    @patch.object(Golds, 'get_random_golds',
                  return_value=MagicMock(return_value=[]))
    def test_with_train_split(self, mock):

        c = Control()
        c.gold_getter.random(100)
        c.get_gold_labels()

        mock.assert_called_with(100)

    @patch.object(Golds, 'get_golds',
                  return_value=MagicMock(return_value=[]))
    def test_without_train_split(self, mock):
        c = Control()
        c.get_gold_labels()

        mock.assert_called_with()


# def test_classifications_projection():
#     q = Query()
#     q.fields(['user_id', 'classification_id'])
#     raw = dbcl.classifications.aggregate(q.build())

#     item = raw.next()

#     assert 'user_id' in item
#     assert 'classification_id' in item
#     assert 'subject_id' not in item


# def test_classifications_limit():
#     q = Query()
#     q.fields(fields).limit(5)
#     raw = dbcl.classifications.aggregate(q.build())

#     assert len(list(raw)) == 5


# def test_users():
#     control = swap.Server(.5, .5)
#     users = control.getClassificationsByUser()

#     pprint(list(users))


@pytest.mark.skip(reason='Network call, takes too long')
def test_get_one_classification():
    """ Get the first classification
    """
    control = Control(0.5, 0.5)

    cursor = control.get_classifications()
    n_class = len(cursor)
    cl = cursor.next()

    assert n_class > 0
    assert type(cl) == dict
    assert len(cl) > 0


class TestGoldGetter:

    @patch.object(Golds, 'get_golds',
                  MagicMock(return_value=[]))
    def test_wrapper_golds_to_None(self):
        gg = GoldGetter()
        gg._golds = {}
        gg.all()

        assert gg._golds is None

    @patch.object(Golds, 'get_golds',
                  MagicMock(return_value=[]))
    def test_wrapper_getter(self):
        gg = GoldGetter()
        gg._golds = {}
        gg.all()

        print(gg.getters)
        assert callable(gg.getters[0])

    def test_getter_propagation(self):
        c = Control()
        c.gold_getter.getters = [lambda: {1: 1, 2: 0}]

        c.init_swap()
        assert c.swap.subjects.get(1).gold == 1
        assert c.swap.subjects.get(2).gold == 0

    def test_multiple_getters(self):
        c = Control()
        c.gold_getter.getters = [
            lambda: {1: 1, 2: 0},
            lambda: {3: 0, 4: 0}
        ]

        c.init_swap()
        assert c.swap.subjects.get(1).gold == 1
        assert c.swap.subjects.get(2).gold == 0
        assert c.swap.subjects.get(3).gold == 0
        assert c.swap.subjects.get(4).gold == 0

    @pytest.mark.skip(reason='Network call, takes too long')
    def test_real_multiple_getters(self):
        c = Control()
        gg = c.gold_getter

        gg.controversial(10)
        gg.consensus(10)

        golds = c.get_gold_labels()
        print(golds)
        assert len(golds) == 20

    def test_reset(self):
        c = Control()
        gg = c.gold_getter
        gg.getters = [lambda: {1: 1, 2: 0}]
        gg.golds
        assert gg._golds is not None

        gg.reset()
        assert gg._golds is None
