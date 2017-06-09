################################################################
#

from swap.db import classifications as dbcl
import swap.config as config


__doc__ = """
    Ranks subjects by how controversial or agreeable they are
"""


def _controv_query(size=100, version='pow'):
    return [
        {
            '$group': {
                '_id': '$subject_id',
                'total': {'$sum': 1},
                'real': {'$sum': {'$cond': [{'$eq': ['$annotation', 1]},
                                            1, 0]}},
                'bogus': {'$sum': {'$cond': [{'$eq': ['$annotation', 0]},
                                             1, 0]}}
            }
        },
        {
            '$project': {
                '_id': 1, 'real': 1, 'bogus': 1, 'total': 1, 'controversy': {
                    '$cond': [
                        {'$gt': ['$real', '$bogus']},
                        {'$%s' % version: [
                            {'$add': ['$real', '$bogus']},
                            {'$divide': ['$bogus', '$real']}]},
                        {'$%s' % version: [
                            {'$add': ['$real', '$bogus']},
                            {'$divide': ['$real', '$bogus']}]}
                    ]
                }
            }
        },
        # {
        #     '$match': {
        #         'total': {'$lt': 50}
        #     }
        # },
        {
            '$sort': {
                'controversy': -1
            }
        },
        {
            '$limit': size
        }
    ]


def _consensus_query(size=100, version='pow'):
    return [
        {
            '$group': {
                '_id': '$subject_id',
                'total': {'$sum': 1},
                'real': {'$sum': {'$cond': [{'$eq': ['$annotation', 1]},
                                            1, 0]}},
                'bogus': {'$sum': {'$cond': [{'$eq': ['$annotation', 0]},
                                             1, 0]}}
            }
        },
        {
            '$project': {
                '_id': 1, 'real': 1, 'bogus': 1, 'total': 1, 'consensus': {
                    '$cond': [
                        {'$gt': ['$real', '$bogus']},
                        {'$%s' % version: [
                            {'$abs': {'$subtract': ['$real', '$bogus']}},
                            {'$subtract':
                                [1, {'$divide': ['$bogus', '$real']}]}]},
                        {'$%s' % version: [
                            {'$abs': {'$subtract': ['$real', '$bogus']}},
                            {'$subtract':
                                [1, {'$divide': ['$real', '$bogus']}]}]},
                    ]
                }
            }
        },
        # {
        #     '$match': {
        #         'total': {'$lt': 50}
        #     }
        # },
        {
            '$sort': {
                'consensus': -1
            }
        },
        {
            '$limit': size
        }
    ]


# def _consensus_max_query(min_):
#     return [
#         {
#             '$group': {
#                 '_id': '$subject_id',
#                 'total': {'$sum': 1},
#                 'real': {'$sum': {'$cond': [{'$eq': ['$annotation', 1]},
#                                             1, 0]}},
#                 'bogus': {'$sum': {'$cond': [{'$eq': ['$annotation', 0]},
#                                              1, 0]}}
#             }
#         },
#         {
#             '$project': {
#                 '_id': 1, 'real': 1, 'bogus': 1, 'total': 1, 'controv': {
#                     '$cond': [
#                         {'$gt': ['$real', '$bogus']},
#                         {'$pow': [
#                             {'$abs': {'$subtract': ['$real', '$bogus']}},
#                             {'$subtract':
#                                 [1, {'$divide': ['$bogus', '$real']}]}]},
#                         {'$pow': [
#                             {'$abs': {'$subtract': ['$real', '$bogus']}},
#                             {'$subtract':
#                                 [1, {'$divide': ['$real', '$bogus']}]}]},
#                     ]
#                 }
#             }
#         },
#         {
#             '$match': {
#                 'controv': {'$gt': min_}
#             }
#         },
#         {
#             '$sort': {
#                 'controv': -1
#             }
#         }
#     ]


def get_controversial(size):
    """
    Get the most controversial subjects

    Formula: :math:`(x + y) ^ {x \over y}` where :math:`x<y`

    Parameters
    ----------
    size : int
        Number of subjects in the set
    """
    version = config.controversial_version
    query = _controv_query(size, version)
    cursor = dbcl.aggregate(query)
    subjects = []
    for item in cursor:
        subjects.append(item['_id'])

    return subjects


def get_consensus(size):
    """
    Get the most agreeable subjects, i.e. subjects with highest consensus

    Formula: :math:`(y-x) ^ {1 - {x \over y}}` where :math:`x<y`

    Parameters
    ----------
    size : int
        Number of subjects in the set
    """
    version = config.controversial_version
    query = _consensus_query(size, version)
    cursor = dbcl.aggregate(query)
    subjects = []
    for item in cursor:
        subjects.append(item['_id'])

    return subjects


# def get_max_consensus(min_):
#     query = _consensus_query(min_)
#     cursor = dbcl.aggregate(query)
#     subjects = []
#     for item in cursor:
#         subjects.append(item['_id'])

#     return subjects
