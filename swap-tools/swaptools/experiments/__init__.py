
from swap import Control
from swap.agents.agent import Stat
from swap.utils.scores import ScoreExport
from swap.config import Config
import swap.ui
import swap.db.experiment as dbe

import json


class Trial:
    def __init__(self, golds, score_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """

        self.golds = golds
        self.scores = score_export

    def plot(self, cutoff):
        # return (self.consensus, self.controversial,
        #         self.purity(cutoff), self.completeness(cutoff))
        pass

    ###############################################################

    def n_golds(self):
        n = {-1: 0, 0: 0, 1: 0}
        for gold in self.golds.values():
            n[gold] += 1

        return n

    def purity(self, cutoff):
        return self.scores.purity(cutoff)

    def completeness(self, cutoff):
        return self.scores.completeness(cutoff)

    def db_export(self, name):
        data = []
        for i in self.scores.sorted_scores:
            score = self.scores.scores[i]
            item = self._db_export_id(name).update({
                'subject': score.id,
                'gold': score.gold,
                'p': score.p,
                'used_gold': -1
            })

            if score.id in self.golds:
                item['used_gold'] = self.golds[score.id]

            data.append(item)

        return data

        # export = {}
        # export['consensus'] = self.consensus
        # export['controversial'] = self.controversial

        # golds = {'0': [], '1': [], '-1': []}
        # for id_, gold in self.golds.items():
        #     golds[str(gold)].append(id_)
        # export['golds'] = golds

        # def score_to_bson(score):
        #     subject, gold, p = score
        #     return {'subject': subject, 'gold': gold, 'score': p}

        # export['scores'] = [score_to_bson(x) for x in self.scores.full()]

        # return export

    @classmethod
    def _db_export_id(cls, name):
        return {'experiment': name}

    # def to_json(self, fname, data={}):
    #     data['golds'] = self.golds
    #     data['scores'] = self.score_export.scores
    #     with open(fname, 'w') as file:
    #         json.dump(data, file)

    # @classmethod
    # def from_json(cls, fname):
    #     with open(fname) as file:
    #         data = json.load(file)

    #     return cls.parse_json(data)

    # @classmethod
    # def parse_json(cls, data):
    #     golds = data['golds']
    #     scores = ScoreExport(data['scores'])

    #     return Trial(golds, scores)


class Experiment:
    def __init__(self, cutoff=0.96):
        self.trials = []
        self.plot_points = []

        self.p_cutoff = cutoff

    def run(self, saver):
        pass

    def plot(self, fname):
        pass

    ###############################################################

    @staticmethod
    def from_trial_export(directory, cutoff, loader):
        files = get_trials(directory)

        e = Experiment(cutoff)
        for fname in files:
            print(fname)
            trials = loader(fname)
            for trial in trials:
                e.add_trial(trial, keep=False)
            e.trials = []

        return e

    @classmethod
    def init_swap(cls):
        control = Control()
        control.run()

        return control.getSWAP()

    def clear_mem(self, saver, fname):
        """
            Saves trial objects to disk to free up memory
        """
        saver(self.trials, fname)
        self.trials = []

    def add_trial(self, trial, keep=True):
        if keep:
            self.trials.append(trial)
        self.plot_points.append(trial.plot(self.p_cutoff))

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s


def upload_trials(directory, loader):
    files = get_trials(directory)
    for fname in files:
        print(fname)
        trials = loader(fname)
        dbe.upload_trials(trials)


def get_trials(directory):
    import os
    import re

    pattern = re.compile('trials_cv_[0-9]{1,4}_cn_[0-9]{1,4}.pkl')

    def _path(fname):
        return os.path.join(directory, fname)

    def istrial(fname):
        if pattern.match(fname):
            return True
        else:
            return False

    files = []
    for fname in os.listdir(directory):
        path = _path(fname)
        if os.path.isfile(path) and istrial(fname):
            files.append(path)

    return files


class ExperimentInterface(swap.ui.Interface):

    def options(self, parser):

        parser.add_argument(
            '--run', nargs=2,
            metavar=('trials directory, experiment file'))

        parser.add_argument(
            '--cutoff', nargs=1,
            help='p cutoff')

        parser.add_argument(
            '--from-trials', nargs=1,
            metavar='directory with trial files',
            help='load experiment plot data from trial files')

        parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='load pickled experiment data')

        parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='pickle and save experiment data')

        parser.add_argument(
            '--shell', action='store_true',
            help='Drop to python interpreter after loading experiment')

        parser.add_argument(
            '--plot', nargs=2,
            metavar=('type', 'file'),
            help='Generate experiment plot')

        parser.add_argument(
            '--pow', action='store_true',
            help='controversial and consensus aggregation method')

        parser.add_argument(
            '--multiply', action='store_true',
            help='controversial and consensus aggregation method')

        # parser.add_argument(
        #     '--upload', nargs=1,
        #     metavar='directory containing trial files',
        #     help='Upload trials to mongo database')

    def call(self, args):
        if args.cutoff:
            cutoff = float(args.cutoff[0])
        else:
            cutoff = 0.96

        config = Config()
        if args.pow:
            config.controversial_version = 'pow'
        elif args.multiply:
            config.controversial_version = 'multiply'

        if args.run:
            e = self._run(args)

        elif args.from_trials:
            e = Experiment.from_trial_export(
                args.from_trials[0],
                cutoff, self.save, self.load)

        elif args.load:
            e = self.load(args.load[0])

        if args.plot:
            self._plot(e, args)

        if args.shell:
            import code
            code.interact(local=locals())

        if args.save:
            assert e
            self.save(e, self.f(args.save[0]))