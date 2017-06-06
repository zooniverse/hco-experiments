
import swap.plots.distributions as distributions
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat
from swap.utils.scores import Score, ScoreExport

import swaptools.experiments.experiment as experiment
import swaptools.experiments.db.experiment_data as dbe

import os


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

    def _db_export_id(self):
        return {
            'controversial': self.controversial,
            'consensus': self.consensus
        }

    @classmethod
    def _parse_db_data(cls, db_data, kwargs=None):
        kwargs = super()._parse_db_data(db_data, kwargs)
        kwargs['consensus'] = db_data['id']['consensus']
        kwargs['controversial'] = db_data['id']['consensus']

        return kwargs


class Experiment(experiment.Experiment):

    def __init__(self, name, cutoff=0.96,
                 consensus=None, controversial=None):
        super().__init__(name, cutoff)

        if consensus is None:
            consensus = (0, 2001, 50)
        if controversial is None:
            controversial = (0, 2001, 50)

        self.consensus = consensus
        self.controversial = controversial

    def run(self):
        gg = GoldGetter()
        swap = self.init_swap()
        n = 1
        for cv in range(*self.controversial):
            for cn in range(*self.consensus):
                if cv == 0 and cn == 0:
                    continue
                gg.reset()

                print('\nRunning trial %d with cv=%d cn=%d' %
                      (n, cv, cn))
                if cv > 0:
                    gg.controversial(cv)
                if cn > 0:
                    gg.consensus(cn,)

                swap.set_gold_labels(gg.golds)
                swap.process_changes()
                self.add_trial(Trial(cn, cv, gg.golds, swap.score_export()))

                n += 1

    def plot(self, type_, fname):
        if type_ == 'purity':
            self.plot_purity(fname)
        elif type_ == 'completeness':
            self.plot_completeness(fname)
        elif type_ == 'both':
            self.plot_both(fname)

    @classmethod
    def build_from_db(cls, experiment_name, cutoff):
        e = cls(experiment_name, cutoff=cutoff)
        for trial_info, golds, scores in dbe.get_trials(experiment_name):
            scores = [(id_, Score(id_, gold, p)) for id_, gold, p in scores]
            scores = ScoreExport(dict(scores), new_golds=False)

            cv = trial_info['controversial']
            cn = trial_info['consensus']

            trial = Trial(cn, cv, golds, scores)
            e.add_trial(trial, keep=False)

        return e

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

    def _run(self, args):
        d_trials = self.f(args.run[0])
        f_pickle = self.f(args.run[1])

        cn = None
        cv = None

        if args.consensus:
            _, b, c = args.consensus
            cn = (1, b + 1, c)

        if args.controversial:
            _, b, c = args.controversial
            cv = (1, b + 1, c)

        def saver(trials, fname):
            fname = os.path.join(d_trials, fname)
            self.save(trials, fname)

        e = Experiment(controversial=cv, consensus=cn)
        e.run()

        self.save(e, f_pickle)

        return e

    def _plot(self, e, args):
        assert e
        fname = self.f(args.plot[1])
        type_ = args.plot[0]

        e.plot(type_, fname)

    @staticmethod
    def _from_db(name, cutoff):
        return Experiment.build_from_db(name, cutoff)


if __name__ == "__main__":
    pass
