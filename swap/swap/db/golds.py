
from swap.db import DB
import swap.db.classifications as dbc

import sys
from functools import wraps
import logging
logger = logging.getLogger(__name__)

collection = DB().subjects


def aggregate(*args, **kwargs):
    try:
        logger.debug('Preparing to run aggregation')
        logger.debug(*args, **kwargs)
        return collection.aggregate(*args, **kwargs)
    except Exception as e:
        logger.error(e)
        raise e


def parse_golds(func):
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

    @wraps(func)
    def wrapper(*args, type_=dict, **kwargs):
        # build cursor from query
        query = func(*args, **kwargs)
        # add pipelines to use most recent gold entry
        # of each subject, and propery projections
        query += _selection()
        cursor = aggregate(query)

        if type_ is dict:
            data = {}
            for item in cursor:
                id_ = item['subject']
                gold = item['gold']

                data[id_] = gold
        elif type_ is tuple:
            data = []
            for item in cursor:
                data.append((item['subject'], item['gold']))
        else:
            raise TypeError("type_ '%s' invalid type!" % str(type_))

        return data
    return wrapper


# def _projection():
#     return [{'$project': {'subject': 1, 'gold': 1}}]


def _selection():
    return [
        {'$group': {'_id': '$subject', 'gold': {'$last': '$gold'}}},
        {'$project': {'subject': '$_id', 'gold': 1}}]


@parse_golds
def get_golds(subjects=None):
    query = []
    if subjects is not None:
        query += [{'$match': {'subject': {'$in': subjects}}}]

    return query


@parse_golds
def get_random_golds(size):
    query = [
        {'$match': {'gold': {'$ne': -1}}},
        {'$sample': {'size': size}}]

    return query


def build_from_classifications():
    data = []
    count = 0
    logger.info('querying for subject gold data')
    for subject, gold in dbc.getAllGolds(type_=tuple):
        data.append({'subject': subject, 'gold': gold})

        count += 1
        sys.stdout.write('\r%d' % count)
        sys.stdout.flush()

    logger.info('Uploading subject data')
    collection.insert_many(data)
