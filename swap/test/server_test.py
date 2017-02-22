#!/usr/bin/env python
################################################################
# Script to test server functionality

import swap
from swap.mongo.query import Query
from pprint import pprint
import time

# server = swap.Server(.5,.5)

# print(server.getClassifications())

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
#     server = swap.Server(.5, .5)
#     users = server.getClassificationsByUser()

#     pprint(list(users))


def test_get_one_classification():
    """ Get the first classification
    """
    server = swap.Server(0.5, 0.5)

    classification_cursor = server.classifications.find()
    n_class = classification_cursor.count()
    current_classification = classification_cursor.next()

    assert n_class > 0
    assert type(current_classification) == dict
    assert len(current_classification) > 0


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
    server = swap.Server(.5, .5)
    start = time.time()
    server.getSubjects()
    print("--- %s seconds ---" % (time.time() - start))

    server = swap.Server(.5, .5)
    start = time.time()
    server.getSubjects2()
    print("--- %s seconds ---" % (time.time() - start))


def main_duration_iterate_classifications(n_classifications=1000):
    """ Measure duration to iteratively read N classifications to memory
        This reads one classification at a time
    """
    server = swap.Server(.5, .5)
    start = time.time()
    # loop over cursor to retrieve classifications
    for i in range(0, n_classifications):
        classification_cursor = server.classifications.find()
        current_classification = classification_cursor.next()
    print("--- %s seconds ---" % (time.time() - start))


def main_duration_batch_classifications(n_classifications=1000,
                                        max_batch_size=1000):
    """ Meausre time to read N classifications in batches of max size M
    """
    server = swap.Server(.5, .5)
    start = time.time()
    # initialize curser with limit and max batch size
    classification_cursor = server.classifications.find().limit(n_classifications).batch_size(min(max_batch_size,n_classifications))
    # loop over cursor to retrieve classifications
    for i in range(0, n_classifications):
        current_classification = classification_cursor.next()
    print("--- %s seconds ---" % (time.time() - start))


def run_server():
    server = swap.Server(.5, .5)
    server.process()


if __name__ == "__main__":
    main_duration_batch_classifications(n_classifications=1000,max_batch_size=1000)
    main_duration_iterate_classifications(n_classifications=10)

    run_server()
    #main_duration()
    # test_users()

