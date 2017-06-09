import swap.plots.distributions as distributions
from swap.utils.golds import GoldGetter
from swap.agents.agent import Stat

import swaptools.experiments.experiment as experiment

import logging

logger = logging.getLogger(__name__)
plt = distributions.plt
mpl = distributions.mpl


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

    def plot(self, cutoff):
        return (len(self.golds), self.n,
                self.purity(cutoff), self.completeness(cutoff))

    def _db_export_id(self):
        return {'n': self.n, 'golds': len(self.golds)}


class Experiment(experiment.Experiment):

    def __init__(self, name, cutoff, num_golds=None, num_trials=10):
        super().__init__(name, cutoff)

        if num_golds is None:
            num_golds = (1000, 2001, 1000)

        self.num_golds = num_golds
        self.num_trials = num_trials

    def _run(self):
        gg = GoldGetter()
        swap = self.init_swap()
        for n_golds in range(*self.num_golds):
            for n in range(self.num_trials):

                gg.reset()
                gg.random(n_golds)

                logger.debug('Running trial %d with %d golds', n, n_golds)
                logger.debug('Real n golds: %d' % len(gg.golds))
                fake = 0
                for gold in gg.golds.values():
                    if gold == -1:
                        fake += 1
                logger.debug('Fake n golds: %d' % fake)

                swap.set_gold_labels(gg.golds)
                swap.process_changes()
                self.add_trial(Trial(n, gg.golds, swap.score_export()))

    @classmethod
    def trial_from_db(cls, trial_info, golds, scores):
        n = trial_info['n']
        return Trial(n, golds, scores)

    def plot(self, type_, fname):
        plt.subplot(111)
        data = sorted(self.plot_points, key=lambda item: (item[0]//1000, item[2]))
        # x, y, z, _ = zip(*data)
        min_c = min(data, key=lambda item: item[2])[2]
        max_c = max(data, key=lambda item: item[2])[2]
        norm = mpl.colors.Normalize(vmin=min_c, vmax=max_c)
        y = 0
        last = 0
        for point in data:
            golds, n, p, _ = point
            if last // 1000 < golds // 1000:
                last = golds
                y = 0
            plt.scatter(golds, y, c=p, norm=norm, cmap='viridis')
            print(golds, n, p)
            y += 1


        data = sorted(self.plot_points, key=lambda item: (item[0]//1000, item[3]))
        # x, y, z, _ = zip(*data)
        min_c = min(data, key=lambda item: item[3])[3]
        max_c = max(data, key=lambda item: item[3])[3]
        norm = mpl.colors.Normalize(vmin=min_c, vmax=max_c)
        y = 0
        last = 0
        for point in data:
            golds, n, _, c = point
            if last // 1000 < golds // 1000:
                last = golds
                y = 0
            plt.scatter(golds, y, c=c, norm=norm, cmap='viridis')
            print(golds, n, c)
            y -= 1

        plt.show()

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

        parser.add_argument(
            '--num-golds', nargs=3)

    def _run(self, name, cutoff, args):
        kwargs = {}
        if args.n:
            kwargs['num_trials'] = int(args.n[0])

        if args.num_golds:
            golds = [int(i) for i in args.num_golds]
            golds[1] += 1    # To ensure range() includes upper limit
            kwargs['num_golds'] = tuple(golds)

        e = Experiment(name, cutoff, **kwargs)
        e.run()

        return e

    @staticmethod
    def _from_db(name, cutoff):
        return Experiment.build_from_db(name, cutoff)

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
