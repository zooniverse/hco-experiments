#!/usr/bin/env python
################################################################
# Script to test db functionality

from swap.db import classifications as dbcl
from swap.db import DB, Cursor
from swap.db.query import Query
from unittest.mock import MagicMock

import pymongo


class Test_DB:

    def test_get_classifications_1(self):
        mock = MagicMock()
        dbcl.collection = mock

        q = Query().project(
            ['user_name', 'subject_id', 'annotation'])

        dbcl.getClassifications()

        mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    # def test_get_classifications_2(self):
    #     db = DB()
    #     mock = MagicMock()
    #     db.classifications = mock

    #     q = Query().project(
    #         ['user_name', 'subject_id', 'annotation'])

    #     db.getClassifications(gold=False)

    #     mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    def test_get_classifications_3(self):
        mock = MagicMock()
        dbcl.collection = mock

        q = Query().project(
            ['a', 'b', 'c'])

        dbcl.getClassifications(q)

        mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    def test_batch_size(self):
        mock = MagicMock()
        dbcl.collection = mock

        db = DB()
        db.setBatchSize(42)

        q = Query().project(
            ['a', 'b', 'c'])

        dbcl.getClassifications(q)

        mock.aggregate.assert_called_with(q.build(), batchSize=42)


class Test_Cursor:
    def test_length(self):
        DB._instances = {}
        db = DB()
        query = [{'$limit': 5}]

        c = Cursor(query, db.classifications)
        print(c.next())

        assert len(c) == 5

    def test_get_cursor_type(self):
        DB._instances = {}
        db = DB()
        query = [{'$limit': 5}]

        c = Cursor(query, db.classifications)

        assert isinstance(c.getCursor(), pymongo.command_cursor.CommandCursor)


class TestClassifications:

    def test_batch_size(self):
        old = dbcl.collection

        mock = MagicMock()
        dbcl.collection = mock
        dbcl.getClassifications(batch_size=50)

        args, kwargs = mock.aggregate.call_args
        assert 'batchSize' in kwargs
        assert kwargs['batchSize'] == 50

        dbcl.collection = old

    def test_gold_from_cursor_dict(self):
        data = [(1, 1), (2, 1), (3, 0), (4, 0)]
        cursor = [{'_id': i[0], 'gold': i[1]} for i in data]

        labels = dbcl.goldFromCursor(cursor, type_=dict)
        print('labels: %s, data: %s' % (str(labels), str(data)))
        for id_, gold in data:
            assert labels[id_] == gold

    def test_gold_from_cursor_tuple(self):
        data = [(1, 1), (2, 1), (3, 0), (4, 0)]
        cursor = [{'_id': i[0], 'gold': i[1]} for i in data]

        labels = dbcl.goldFromCursor(cursor, type_=tuple)
        print('labels: %s, data: %s' % (str(labels), str(data)))
        print(labels)
        for i, item in enumerate(data):
            assert labels[i] == item
