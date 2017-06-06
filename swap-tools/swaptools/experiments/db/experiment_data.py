################################################################
# Methods for experiment collection

from swaptools.experiments.db import DB
from swap.db import Cursor

import sys

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
        self.current_trial = None

    @property
    def trials(self):
        if self._trials is None:
            print('generating list of trials')
            query = [
                {'$match': {'experiment': self.name}},
                {'$sort': {'trial': 1}}
            ]

            self._trials = Cursor(query, collection, allowDiskUse=True)
            self.current_trial = self._trials.next()
            print('done')
        return self._trials

    def parse_trial(self):
        cursor = self.trials
        item = self.current_trial

        scores = []
        golds = {}
        trial_info = item['trial']
        print('parsing trial %s' % trial_info)

        n = 0
        while item['trial'] == trial_info:
            p = item['p']
            gold = item['gold']
            _id = item['subject']

            if item['used_gold'] in [0, 1]:
                golds[_id] = item['used_gold']

            # score = Score(_id, gold, p)
            scores.append((_id, gold, p))

            item = cursor.next()
            n += 1

            if n % 100 == 0:
                sys.stdout.write('\r%d' % n)
                sys.stdout.flush()

        print('\ndone')

        self.current_trial = item
        return trial_info, golds, scores

    # def get_trial(self, trial_info):
    #     print('getting trial %s' % trial_info)
    #     query = [
    #         {'$match': {'experiment': self.name, 'trial': trial_info}}
    #     ]

    #     cursor = Cursor(query, collection, allowDiskUse=True)
    #     print('done')
    #     return self.parse_trial(cursor)

    def next(self):
        return self.parse_trial()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return len(self.trials)
