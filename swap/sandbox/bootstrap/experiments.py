
import swap.plots.distributions as distributions
from swap import Control


class Trial:
    def __init__(self, consensus, controversial, golds, swap_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """
        self.consensus = consensus
        self.controversial = controversial

        self.golds = golds
        self.scores = swap_export

    def n_golds(self):
        n = {-1: 0, 0: 0, 1: 0}
        for gold in self.golds.values():
            n[gold] += 1

        return n

    def purity(self):
        return self.scores.purity(.96)

    def purify(self):
        pass

    def plot(self):
        return (self.consensus, self.controversial, self.purity())

    @staticmethod
    def from_control(consensus, controversial, control):
        t = Trial(consensus, controversial,
                  control.gold_getter.golds,
                  control.getSWAP().score_export())
        return t


class Experiment:
    def __init__(self, saver):
        self.trials = []
        self.plot_points = []
        self.control = Control(.12, .5)
        self.save_f = saver

    def run(self):
        control = self.control
        n = 1
        for cv in range(0, 1001, 50):
            for cn in range(0, 1001, 50):
                if cv == 0 and cn == 0:
                    continue
                control.reset()

                print('Running trial %d with cv=%d cn=%d' %
                      (n, cv, cn))
                if cv > 0:
                    control.gold_getter.controversial(cv)
                if cn > 0:
                    control.gold_getter.consensus(cn)

                control.process()
                self.trials.append(Trial.from_control(cn, cv, control))

                n += 1
            self.clear_mem(cn, cn)

    def clear_mem(self, cv, cn):
        """
            Saves trial objects to disk to free up memory
        """
        def to_fname(n):
            if type(n) is int:
                return str(n)
            elif type(n) is tuple:
                return '_'.join(n)
            else:
                return ''

        fname = 'trials_cv_%s_cn_%s.pkl' % (cv, cn)
        self.save_f(self.trials, fname)

        for trial in self.trials:
            self.plot_points.append(trial.plot())
        self.trials = []

    def plot(self, fname):
        data = self.plot_points
        distributions.multivar_scatter(fname, data)


if __name__ == "__main__":
    e = Experiment()
    e.run()

    import code
    code.interact(local=locals())

    # x_ = range(50)
    # y_ = range(50)
    # z = lambda x, y: x + y

    # data = []
    # for x in x_:
    #     for y in y_:
    #         data.append((x, y, z(x, y)))

    # print(data)
    # distributions.multivar_scatter(None, data)
