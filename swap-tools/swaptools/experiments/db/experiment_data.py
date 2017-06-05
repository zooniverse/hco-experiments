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


def get_trials(experiment_name):
    return TrialsCursor(experiment_name)
    # assert group
    # query = [
    #     {'$match': {'experiment': experiment_name}},
    #     {'$group': {'_id': {'controversial': '$trial.controversial',
    #                         'consensus': '$trial.consensus'},
    #                 'points': {'$push': {'subject': '$subject',
    #                                      'gold': '$gold',
    #                                      'p': '$p', 'used_gold':
    #                                      '$used_gold'}}}}
    # ]

    # return Cursor(query, collection, allowDiskUse=True)


class TrialsCursor:

    def __init__(self, name):
        self.name = name
        self._trials = None

    @property
    def trials(self):
        if self._trials is None:
            query = [
                {'$match': {'experiment': self.name}},
                {'$group': {'_id': '$trial'}}
            ]

            self._trials = Cursor(query, collection, allowDiskUse=True)
        return self._trials

    @staticmethod
    def parse_trial(cursor):
        scores = {}
        golds = {}
        for item in cursor:
            p = item['p']
            gold = item['gold']
            _id = item['subject']

            if item['used_gold'] in [0, 1]:
                golds[_id] = item['used_gold']

            # score = Score(_id, gold, p)
            score = (_id, gold, p)
            scores[_id] = score

        return golds, scores

    def get_trial(self, trial_info):
        query = [
            {'$match': {'experiment': self.name, 'trial': trial_info}}
        ]

        cursor = Cursor(query, collection, allowDiskUse=True)
        return self.parse_trial(cursor)

    def next(self):
        trial_info = self.trials.next()
        golds, scores = self.get_trial(trial_info)

        return trial_info, golds, scores

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.trials)
