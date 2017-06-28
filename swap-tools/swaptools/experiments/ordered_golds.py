
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat

import swaptools.experiments.experiment as experiment
import swaptools.experiments.random_golds as randomex

from collections import OrderedDict
import random
import logging
logger = logging.getLogger(__name__)


class Trial(randomex.Trial):
    @staticmethod
    def _db_id(n, n_golds):
        return OrderedDict([('golds', n_golds), ('n', n)])


class Experiment(randomex.Experiment):
    Trial = Trial

    def __init__(self, name, cutoff, start=5000, end=50000, step=10):
        super().__init__(name, cutoff)

        self.start = start
        self.end = end
        self.step = step

    def _run(self):
        gg = GoldGetter()
        gg.all()

        swap = self.init_swap()
        gi = GoldIterator(gg.golds, self.start, self.step)

        for n, golds in enumerate(gi):

            logger.info('Running trial %d with %d golds', n, len(golds))
            fake = 0
            for gold in golds.values():
                if gold == -1:
                    fake += 1
            logger.debug('Fake n golds: %d', fake)

            swap.set_gold_labels(golds)
            swap.process_changes()
            self.add_trial(randomex.Trial(n, golds, swap.score_export()))

            if len(golds) > self.end:
                break

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s

    def __repr__(self):
        s = 'Ordered golds experiment %d golds %d trials' % \
            (self.num_golds, self.num_trials)
        return s


class GoldIterator:

    def __init__(self, golds, start, step):
        self.golds = self.filter_golds(golds.copy())
        self.order = self.shuffle(self.golds)
        self.step = step
        self.i = start

    @staticmethod
    def shuffle(golds):
        golds = list(golds.keys())
        return list(sorted(golds, key=lambda _: random.random()))

    @staticmethod
    def filter_golds(golds):
        for subject in golds.copy():
            if golds[subject] == -1:
                del golds[subject]
        return golds

    def next(self):
        golds = {}
        i = self.i
        step = self.step
        for key in self.order[0: i + step]:
            golds[key] = self.golds[key]

        self.i += self.step

        return golds

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


class Interface(randomex.Interface):
    Experiment = Experiment

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        return 'ordered'

    def options(self, parser):
        """
        Add options to the parser
        """
        super().options(parser)

        parser.add_argument(
            '--step', nargs=1)

        parser.add_argument(
            '--start', nargs=1)

        parser.add_argument(
            '--end', nargs=1)

    def _run(self, name, cutoff, args):
        kwargs = {}
        if args.step:
            kwargs['step'] = int(args.step[0])

        if args.start:
            kwargs['start'] = int(args.start[0])

        if args.end:
            kwargs['end'] = int(args.end[0])

        e = Experiment(name, cutoff, **kwargs)
        e.run()

        return e

    @staticmethod
    def _from_db(name, cutoff):
        return Experiment.build_from_db(name, cutoff)

    def _build_trial(self, trial_info, golds, scores):
        return Trial.build_from_db(trial_info, golds, scores)

    @staticmethod
    def _trial_kwargs(trial_args):
        n = int(trial_args[0])
        golds = int(trial_args[1])
        return Trial._db_id(n, golds)
