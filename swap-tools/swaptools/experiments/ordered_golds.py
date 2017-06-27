
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat

import swaptools.experiments.experiment as experiment
import swaptools.experiments.random_golds as randomex

import random
import logging
logger = logging.getLogger(__name__)


class Experiment(randomex.Experiment):

    def __init__(self, name, cutoff, step=10):
        super().__init__(name, cutoff)

        self.step = step

    def _run(self):
        gg = GoldGetter()
        gg.all()

        swap = self.init_swap()
        for n, golds in enumerate(GoldIterator(gg.golds, self.step)):

            logger.info('Running trial %d with %d golds', n, len(golds))
            fake = 0
            for gold in golds.values():
                if gold == -1:
                    fake += 1
            logger.debug('Fake n golds: %d', fake)

            swap.set_gold_labels(golds)
            swap.process_changes()
            self.add_trial(randomex.Trial(n, golds, swap.score_export()))

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s

    def __repr__(self):
        s = 'Ordered golds experiment %d golds %d trials' % \
            (self.num_golds, self.num_trials)
        return s


class GoldIterator:

    def __init__(self, golds, step):
        self.golds = self.filter_golds(golds.copy())
        self.order = self.shuffle(self.golds)
        self.step = step + 1
        self.i = 0

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


class Interface(experiment.ExperimentInterface):

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

    def _run(self, name, cutoff, args):
        kwargs = {}
        if args.step:
            kwargs['step'] = int(args.step[0])

        e = Experiment(name, cutoff, **kwargs)
        e.run()

        return e

    @staticmethod
    def _from_db(name, cutoff):
        return Experiment.build_from_db(name, cutoff)
