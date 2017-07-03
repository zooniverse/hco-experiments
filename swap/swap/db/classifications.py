################################################################
# Methods for classification collection

"""
    Manages interactions with the classification collection in the database.

    Module level variables:
        collection
            collection this module acts on
        aggregate
            reference to the pymongo aggregation method of the collection
"""

from swap.db import DB, Cursor
from swap.db.query import Query
import swap.utils.parsers as parsers
import swap.config as config

from collections import OrderedDict

import sys
import csv
import logging
logger = logging.getLogger(__name__)

subject_count = None
collection = DB().classifications


def aggregate(*args, **kwargs):
    try:
        logger.debug('Preparing to run aggregation')
        logger.debug(*args, **kwargs)
        return collection.aggregate(*args, **kwargs)
    except Exception as e:
        logger.error(e)
        raise e


def getClassifications(query=None, **kwargs):
    """
    Returns all classifications.

    Useful when running simulations of SWAP, as it returns all
    available data at once.

    Parameters
    ----------
    query : list
        Use a custom query instead
    **kwargs
        Any other variables to pass to mongo, like
        allowDiskUse, batchSize, etc
    """
    # Generate a default query if not specified

    # TODO: Parse session id if no user_id exists
    query = [
        {'$sort': OrderedDict([('seen_before', 1), ('classification_id', 1)])},
        {'$match': {'seen_before': False}},
        # {'$match': {'classification_id': {'$lt': 25000000}}},
        {'$project': {'user_id': 1, 'subject_id': 1,
                      'annotation': 1, 'session_id': 1}}
    ]

    # set batch size as specified in kwargs,
    # or default to the config default
    if 'batch_size' in kwargs:
        batch_size = kwargs['batch_size']
    else:
        batch_size = DB().batch_size

    # perform query on classification data
    classifications = Cursor(query, collection,
                             batchSize=int(1e5))

    return classifications


def goldFromCursor(cursor, type_=dict):
    """
    Generates subject to gold mapping from a cursor

    Iterates through a cursor and parses out the subject to gold
    mappings.

    Parameters
    ----------
    cursor : swap.db.Cursor
        cursor containing data. Should be an aggregation containing
        one document per subject, and with the fields _id mapped to
        subject_id and gold mapped to the appropriate gold label.
    type_ : return type
        Choose the return type. Choices are:

        dict
            {_id : gold}
        tuple
            (_id, gold)
    """
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
    """
    Get gold labels for specific subjects

    Parameters
    ----------
    subjects : list
        List of subject ids
    type_ : return type
        Choose the return type. Choices are:

        dict
            {_id : gold}
        tuple
            (_id, gold)
    """
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$match': {'_id': {'$in': subjects}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getAllGolds(*args, type_=dict):
    """
    Get gold labels for all subjects

    Parameters
    ----------
    type_ : return type
        Choose the return type. Choices are:

        dict
            {_id : gold}
        tuple
            (_id, gold)
    """
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getRandomGoldSample(size, *args, type_=dict):
    """
    Get gold labels for a random sample of subjects

    Parameters
    ----------
    size : int
        Number of subjects in the sample
    type_ : return type
        Choose the return type. Choices are:

        dict
            {_id : gold}
        tuple
            (_id, gold)
    """
    query = [
        {'$group': {'_id': '$subject_id',
                    'gold': {'$first': '$gold_label'}}},
        {'$match': {'gold': {'$ne': -1}}},
        {'$sample': {'size': size}}]

    cursor = aggregate(query)
    return goldFromCursor(cursor, type_)


def getNSubjects():
    """
    Count how many subjects are in the collection
    """
    global subject_count
    if subject_count is None:
        query = [
            {'$group': {'_id': '', 'num': {'$sum': 1}}}]
        cursor = aggregate(query)
        subject_count = cursor.next()['num']

    return subject_count


def upload_project_dump(fname):
    logger.info('dropping collection')
    DB()._db.classifications.drop()
    DB()._init_classifications()

    logger.info('parsing csv dump')
    data = []
    pp = parsers.ClassificationParser(config.database.builder)

    with open(fname, 'r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            cl = pp.process(row)
            data.append(cl)

            sys.stdout.flush()
            sys.stdout.write("%d records processed\r" % i)

            if len(data) > 100000:
                collection.insert_many(data)
                data = []

    collection.insert_many(data)
    DB()._gen_stats()
    logger.debug('done')
