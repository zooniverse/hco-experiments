import swap.plots.distributions as distributions
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat

import swaptools.experiments.experiment as experiment


class Trial(experiment.Trial):
    def __init__(self, n, golds, swap_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """
        super().__init__(golds, swap_export)

        self.n = n

    # def plot(self, cutoff):
    #     return (self.consensus, self.controversial,
    #             self.purity(cutoff), self.completeness(cutoff))

    def _db_export_id(self):
        return {'n': self.n}


class Experiment(experiment.Experiment):

    def __init__(self, name, cutoff, num_golds=1000, num_trials=10):
        super().__init__(name, cutoff)

        self.num_golds = num_golds
        self.num_trials = num_trials

    def run(self):
        gg = GoldGetter()
        swap = self.init_swap()
        for n in range(self.num_trials):

            gg.reset()
            gg.random(self.num_golds)

            print('\nRunning trial %d' % n)

            swap.set_gold_labels(gg.golds)
            swap.process_changes()
            self.add_trial(Trial(n, gg.golds, swap.score_export()))

    @classmethod
    def trial_from_db(cls, trial_info, golds, scores):
        n = trial_info['n']
        return Trial(n, golds, scores)

    # def plot(self, type_, fname):
    #     if type_ == 'purity':
    #         self.plot_purity(fname)
    #     elif type_ == 'completeness':
    #         self.plot_completeness(fname)
    #     elif type_ == 'both':
    #         self.plot_both(fname)

    # def plot_purity(self, fname):
    #     data = []
    #     for point in self.plot_points:
    #         x, y, purity, completeness = point
    #         data.append((x, y, purity))

    #     distributions.multivar_scatter(
    #         fname, data, 'Purity in subjects with p>%.2f' % self.p_cutoff)

    # def plot_completeness(self, fname):
    #     data = []
    #     for point in self.plot_points:
    #         x, y, purity, completeness = point
    #         data.append((x, y, completeness))

    #     import pprint
    #     pprint.pprint(data)
    #     distributions.multivar_scatter(
    #         fname, data,
    #         'Completeness in swap scores when purity >%.2f' % self.p_cutoff)

    # def plot_both(self, fname):
    #     data = []
    #     for point in self.plot_points:
    #         x, y, purity, completeness = point
    #         data.append((x, y, purity * completeness))

    #     import pprint
    #     pprint.pprint(data)
    #     distributions.multivar_scatter(
    #         fname, data, '')

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s

    def __repr__(self):
        s = 'Random grid experiment %d golds %d trials' % \
            (self.num_golds, self.num_trials)
        return s


class Interface(experiment.ExperimentInterface):

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        return 'randomex'

    def options(self, parser):
        """
        Add options to the parser
        """
        super().options(parser)

        parser.add_argument(
            '-n', nargs=1)

    def _run(self, name, cutoff, args):
        kwargs = {}
        if args.n:
            kwargs['num_trials'] = int(args.n[0])

        if args.num_golds:
            kwargs['num_golds'] = int(args.num_golds[0])

        e = Experiment(name, cutoff, **kwargs)
        e.run()

        return e

    # def _plot(self, e, args):
    #     assert e
    #     fname = self.f(args.plot[1])
    #     type_ = args.plot[0]

    #     e.plot(type_, fname)


if __name__ == "__main__":
    # e = Experiment()
    # e.run()

    # import code
    # code.interact(local=locals())

    print(dir())

    # x_ = range(50)
    # y_ = range(50)
    # z = lambda x, y: x + y

    # data = []
    # for x in x_:
    #     for y in y_:
    #         data.append((x, y, z(x, y)))

    # print(data)
    # distributions.multivar_scatter(None, data)
