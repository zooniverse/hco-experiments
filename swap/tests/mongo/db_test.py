#!/usr/bin/env python
################################################################
# Script to test db functionality

from swap.mongo.db import DB
from swap.mongo.query import Query
from unittest.mock import MagicMock


class Test_DB:

    def test_get_classifications_1(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        q = Query().project(
            ['user_name', 'subject_id', 'annotation', 'gold_label'])

        db.getClassifications()

        mock.aggregate.assert_called_with(q.build())

    def test_get_classifications_2(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        q = Query().project(
            ['user_name', 'subject_id', 'annotation'])

        db.getClassifications(gold=False)

        mock.aggregate.assert_called_with(q.build())

    def test_get_classifications_3(self):
        db = DB()
        mock = MagicMock()
        db.classifications = mock

        q = Query().project(
            ['a', 'b', 'c'])

        db.getClassifications(fields=['a', 'b', 'c'])

        mock.aggregate.assert_called_with(q.build())
