################################################################
# Methods for classification collection

from swap.db import DB, Cursor
from swap.db.query import Query

subject_count = None
collection = DB().classifications
aggregate = collection.aggregate


def getClassifications(query=None, **kwargs):
    """ Returns Iterator over all Classifications """
    # Generate a default query if not specified
    query = [
        {'$match': {'classification_id': {'$lt': 25000000}}},
        {'$project': {'user_name': 1, 'subject_id': 1, 'annotation': 1}}
    ]

    # set batch size as specified in kwargs,
    # or default to the config default
    if 'batch_size' in kwargs:
        batch_size = kwargs['batch_size']
    else:
        batch_size = DB().batch_size

    # perform query on classification data
    classifications = Cursor(query, collection,
                             batchSize=batch_size)
    # classifications = self.classifications.aggregate(
    #     query.build(), batchSize=batch_size)

    return classifications


def goldFromCursor(cursor, type_=dict):
    if type_ is dict:
        data = {}
        for item in cursor:
            id_ = item['_id']
            gold = item['gold']

            data[id_] = gold
    elif type_ is tuple:
        data = []
        for item in cursor:
            data.append((item['_id'], item['gold']))
    else:
        raise TypeError("type_ '%s' invalid type!" % str(type_))

    return data


def getExpertGold(subjects, *args, type_=dict):
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$match': {'_id': {'$in': subjects}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getAllGolds(*args, type_=dict):
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getRandomGoldSample(size, *args, type_=dict):
    print(1)
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$sample': {'size': size}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getNSubjects():
    global subject_count
    if subject_count is None:
        query = [
            {'$group': {'_id': '', 'num': {'$sum': 1}}}]
        cursor = aggregate(query)
        subject_count = cursor.next()['num']

    return subject_count
