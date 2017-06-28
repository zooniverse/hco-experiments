
import swap.plots.distributions as distributions
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat

import swaptools.experiments.experiment as experiment

from collections import OrderedDict
import logging
logger = logging.getLogger(__name__)


class Trial(experiment.Trial):
    def __init__(self, consensus, controversial, golds, swap_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """
        super().__init__(golds, swap_export)
        self.consensus = consensus
        self.controversial = controversial

    def plot(self, cutoff):
        return (self.consensus, self.controversial,
                self.purity(cutoff), self.completeness(cutoff))

    @staticmethod
    def _db_id(controversial, consensus):
        return OrderedDict([
            ('controversial', controversial),
            ('consensus', consensus)
        ])

    def _db_export_id(self):
        return self._db_id(self.controversial, self.consensus)

    @classmethod
    def build_from_db(cls, trial_info, golds, scores):
        scores = cls.scores_from_db(scores)
        cn = trial_info['consensus']
        cv = trial_info['controversial']

        return cls(cn, cv, golds, scores)


class Experiment(experiment.Experiment):
    Trial = Trial

    def __init__(self, name, cutoff,
                 consensus=None, controversial=None):
        super().__init__(name, cutoff)

        if consensus is None:
            consensus = (0, 2001, 50)
        if controversial is None:
            controversial = (0, 2001, 50)

        self.consensus = consensus
        self.controversial = controversial

    def _run(self):
        gg = GoldGetter()
        swap = self.init_swap()
        n = 1
        for cv in range(*self.controversial):
            for cn in range(*self.consensus):
                if cv == 0 and cn == 0:
                    continue
                gg.reset()

                logger.info('\nRunning trial %d with cv=%d cn=%d',
                            n, cv, cn)
                if cv > 0:
                    gg.controversial(cv)
                if cn > 0:
                    gg.consensus(cn,)

                swap.set_gold_labels(gg.golds)
                swap.process_changes()
                self.add_trial(
                    self.Trial(cn, cv, gg.golds, swap.score_export()))

                n += 1

    def plot(self, type_, fname):
        if type_ == 'purity':
            self.plot_purity(fname)
        elif type_ == 'completeness':
            self.plot_completeness(fname)
        elif type_ == 'both':
            self.plot_both(fname)

    ###############################################################

    def plot_purity(self, fname):
        data = []
        for point in self.plot_points:
            x, y, purity, _ = point
            data.append((x, y, purity))

        distributions.multivar_scatter(
            fname, data, 'Purity in subjects with p>%.2f' % self.p_cutoff)

    def plot_completeness(self, fname):
        data = []
        for point in self.plot_points:
            x, y, _, completeness = point
            data.append((x, y, completeness))

        import pprint
        pprint.pprint(data)
        distributions.multivar_scatter(
            fname, data,
            'Completeness in swap scores when purity >%.2f' % self.p_cutoff)

    def plot_both(self, fname):
        data = []
        for point in self.plot_points:
            x, y, purity, completeness = point
            data.append((x, y, purity * completeness))

        import pprint
        pprint.pprint(data)
        distributions.multivar_scatter(
            fname, data, '')

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s

    def __repr__(self):
        s = 'Controversial/Consensus grid experiment cv %s cn %s' % \
            (str(self.controversial), str(self.consensus))
        return s


class Interface(experiment.ExperimentInterface):
    Experiment = Experiment

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        return 'cvex'

    def options(self, parser):
        """
        Add options to the parser
        """
        super().options(parser)

        parser.add_argument(
            '--consensus', nargs=3,
            metavar=('min', 'max', 'step'))

        parser.add_argument(
            '--controversial', nargs=3,
            metavar=('min', 'max', 'step'))

    def _run(self, name, cutoff, args):
        cn = None
        cv = None

        if args.consensus:
            _, b, c = args.consensus
            cn = (1, b + 1, c)

        if args.controversial:
            _, b, c = args.controversial
            cv = (1, b + 1, c)

        e = self.Experiment(name, cutoff, controversial=cv, consensus=cn)
        e.run()

        return e

    def _plot(self, e, args):
        assert e
        fname = self.f(args.plot[1])
        type_ = args.plot[0]

        e.plot(type_, fname)


if __name__ == "__main__":
    pass
