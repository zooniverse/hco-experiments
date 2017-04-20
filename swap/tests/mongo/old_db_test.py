#!/usr/bin/env python
################################################################
# Script to test db functionality

from swap.mongo.db import DB, Cursor
from swap.mongo.query import Query
from unittest.mock import MagicMock

import pymongo


class Test_DB:

    def test_get_classifications_1(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        q = Query().project(
            ['user_name', 'subject_id', 'annotation'])

        db.getClassifications()

        mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    # def test_get_classifications_2(self):
    #     db = DB()
    #     mock = MagicMock()
    #     db.classifications = mock

    #     q = Query().project(
    #         ['user_name', 'subject_id', 'annotation'])

    #     db.getClassifications(gold=False)

        mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    def test_get_classifications_3(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        q = Query().project(
            ['a', 'b', 'c'])

        db.getClassifications(q)

        mock.aggregate.assert_called_with(q.build(), batchSize=100000)

    def test_batch_size(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        db.setBatchSize(42)

        q = Query().project(
            ['a', 'b', 'c'])

        db.getClassifications(q)

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
