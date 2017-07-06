#!/usr/bin/env python
################################################################
# Script to test db functionality

from swap.db.classifications import Classifications
from swap.db.db import Collection
from swap.db import DB
from swap.db.db import Cursor
from swap.db.query import Query

from unittest.mock import MagicMock, patch
from collections import OrderedDict

import pymongo

# pylint: disable=R0201


class Test_DB:

    @patch.object(Collection, 'aggregate',
                  return_value=MagicMock())
    def test_get_classifications_1(self, mock):
        query = [
            {'$sort': OrderedDict([
                ('seen_before', 1),
                ('classification_id', 1)])},
            {'$match': {'seen_before': False}},
            {'$project': {
                'user_id': 1, 'subject_id': 1,
                'annotation': 1, 'session_id': 1}}]

        DB().classifications.getClassifications()
        mock.assert_called_with(query, {'batchSize': 100000})

    # def test_get_classifications_2(self):
    #     db = DB()
    #     mock = MagicMock()
    #     db.classifications = mock

    #     q = Query().project(
    #         ['user_name', 'subject_id', 'annotation'])

    #     db.getClassifications(gold=False)

    #     mock.aggregate.assert_called_with(q.build(), batchSize=100000)


class Test_Cursor:
    def test_length(self):
        DB._instances = {}
        db = DB()._db
        query = [{'$limit': 5}]

        c = Cursor(query, db.classifications)
        print(c.next())

        assert len(c) == 5

    def test_get_cursor_type(self):
        DB._instances = {}
        db = DB()._db
        query = [{'$limit': 5}]

        c = Cursor(query, db.classifications)

        assert isinstance(c.getCursor(), pymongo.command_cursor.CommandCursor)


class TestClassifications:

    @patch.object(Collection, 'aggregate', return_value=MagicMock())
    def test_batch_size(self, mock):
        DB().classifications.getClassifications(batch_size=50)

        args, kwargs = mock.call_args
        print(args, kwargs)
        assert 'batchSize' in args[1]
        assert args[1]['batchSize'] == 50

    # def test_gold_from_cursor_dict(self):
    #     data = [(1, 1), (2, 1), (3, 0), (4, 0)]
    #     cursor = [{'_id': i[0], 'gold': i[1]} for i in data]
    #
    #     labels = DB().classifications.goldFromCursor(cursor, type_=dict)
    #     print('labels: %s, data: %s' % (str(labels), str(data)))
    #     for id_, gold in data:
    #         assert labels[id_] == gold
    #
    # def test_gold_from_cursor_tuple(self):
    #     data = [(1, 1), (2, 1), (3, 0), (4, 0)]
    #     cursor = [{'_id': i[0], 'gold': i[1]} for i in data]
    #
    #     labels = DB().classifications.goldFromCursor(cursor, type_=tuple)
    #     print('labels: %s, data: %s' % (str(labels), str(data)))
    #     print(labels)
    #     for i, item in enumerate(data):
    #         assert labels[i] == item
