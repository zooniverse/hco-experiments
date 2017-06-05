################################################################
# Methods for experiment collection

from swaptools.experiments.db import DB
from swap.db import Cursor

collection = DB().data
aggregate = collection.aggregate


def upload_trials(trials, experiment_name):
    data = []
    for trial in trials:
        data += trial.db_export(experiment_name)

    collection.insert_many(data)


def get_trials(experiment_name, group=None):
    assert group
    query = [
        {'$match': {'experiment': experiment_name}},
        {'$group': {'_id': {'controversial': '$trial.controversial',
                            'consensus': '$trial.consensus'},
                    'points': {'$push': {'subject': '$subject',
                                         'gold': '$gold',
                                         'p': '$p', 'used_gold':
                                         '$used_gold'}}}}
    ]

    return Cursor(query, collection, allowDiskUse=True)
