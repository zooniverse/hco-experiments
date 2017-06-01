import swap.plots.distributions as distributions
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat
from swap.config import Config

import os

if __name__ == "__main__":
    import sys
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, '..')
    sys.path.insert(0, path)

import experiments


class Trial(experiments.Trial):
    def __init__(self, n, golds, swap_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """
        super().__init__(golds, swap_export)

        self.n = n

    def plot(self, cutoff):
        return (self.consensus, self.controversial,
                self.purity(cutoff), self.completeness(cutoff))


class Experiment(experiments.Experiment):

    def __init__(self, cutoff=0.96, num_golds=1000, num_trials=10):
        super().__init__(cutoff)

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

            if n > 10:
                self.clear_mem(n)

    def clear_mem(self, n):
        """
            Saves trial objects to disk to free up memory
        """
        fname = 'trials_%d.pkl' % n
        super().clear_mem(fname)

    def plot(self, type_, fname):
        if type_ == 'purity':
            self.plot_purity(fname)
        elif type_ == 'completeness':
            self.plot_completeness(fname)
        elif type_ == 'both':
            self.plot_both(fname)

    def plot_purity(self, fname):
        data = []
        for point in self.plot_points:
            x, y, purity, completeness = point
            data.append((x, y, purity))

        distributions.multivar_scatter(
            fname, data, 'Purity in subjects with p>%.2f' % self.p_cutoff)

    def plot_completeness(self, fname):
        data = []
        for point in self.plot_points:
            x, y, purity, completeness = point
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


class Interface(experiments.ExperimentInterface):

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

    def _run(self, args):
        d_trials = self.f(args.run[0])
        f_pickle = self.f(args.run[1])

        kwargs = {}
        if args.n:
            kwargs['num_trials'] = int(args.n[0])

        if args.num_golds:
            kwargs['num_golds'] = int(args.num_golds[0])

        def saver(trials, fname):
            fname = os.path.join(d_trials, fname)
            self.save(trials, fname)

        e = Experiment(**kwargs)
        e.run(saver)

        self.save(e, f_pickle)

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
