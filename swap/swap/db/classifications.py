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
    if query is None:
        query = Query()

        fields = ['user_name', 'subject_id', 'annotation']
        query.project(fields)

    # set batch size as specified in kwargs,
    # or default to the config default
    if 'batch_size' in kwargs:
        batch_size = kwargs['batch_size']
    else:
        batch_size = DB().batch_size

    # perform query on classification data
    classifications = Cursor(query.build(), collection,
                             batchSize=batch_size)
    # classifications = self.classifications.aggregate(
    #     query.build(), batchSize=batch_size)

    return classifications


def goldFromCursor(cursor):
    data = {}
    for item in cursor:
        id_ = item['_id']
        gold = item['gold']

        data[id_] = gold

    return data


def getExpertGold(subjects):
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$match': {'_id': {'$in': subjects}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor)


def getAllGolds():
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor)


def getRandomGoldSample(size):
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$sample': {'size': size}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor)


def getNSubjects():
    global subject_count
    if subject_count is None:
        query = [
            {'$group': {'_id': '', 'num': {'$sum': 1}}}]
        cursor = aggregate(query)
        subject_count = cursor.next()['num']

    return subject_count
