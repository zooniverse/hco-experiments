#!/usr/bin/env python
################################################################
# Script to test server functionality

import swap
from swap.mongo.query import Query
from pprint import pprint
import time

# server = swap.Server(.5,.5)

# print(server.getClassifications())

fields = {'user_id', 'classification_id', 'subject_id', \
                  'annotation', 'gold_label'}
db = swap.mongo.DB()

def test_classifications_projection():
    q = Query()
    q.fields(['user_id', 'classification_id'])
    raw = db.classifications.aggregate(q.build())

    item = raw.next()

    assert 'user_id' in item
    assert 'classification_id' in item
    assert 'subject_id' not in item

def test_classifications_limit():
    q = Query()
    q.fields(fields).limit(5)
    raw = db.classifications.aggregate(q.build())

    assert len(list(raw)) == 5


def main():
    q = Query()
    q.fields(fields).limit(5)
    print(q.build())
    print(q._project)
    print(fields)
    print(type(fields))


    raw = db.classifications.aggregate(q.build())

    pprint(list(raw))

def main_duration():
    server = swap.Server(.5,.5)
    start = time.time()
    server.getSubjects()
    print("--- %s seconds ---" % (time.time() - start))

    server = swap.Server(.5,.5)
    start = time.time()
    server.getSubjects2()
    print("--- %s seconds ---" % (time.time() - start))

if __name__ == "__main__":
    main_duration()