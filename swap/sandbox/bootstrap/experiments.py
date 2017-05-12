
import swap.plots.distributions as distributions
from swap import Control


class Trial:
    def __init__(self, consensus, controversial, golds, roc_export):
        """
            consensus, controversial: settings used to run swap; number of
                consensus  controversial subjects used to make gold set
            golds: Gold standard set used during run
            roc_export: ScoreExport of swap scores
        """
        self.consensus = consensus
        self.controversial = controversial

        self.golds = golds
        self.roc = roc_export

    def n_golds(self):
        n = {-1: 0, 0: 0, 1: 0}
        for gold in self.golds.values():
            n[gold] += 1

        return n

    def purity(self):
        return self.roc.purity(.96)

    def plot(self):
        return (self.consensus, self.controversial, self.purity())

    @staticmethod
    def from_control(consensus, controversial, control):
        t = Trial(consensus, controversial,
                  control.gold_getter.golds,
                  control.getSWAP().roc_export())
        return t


class Experiment:
    def __init__(self):
        self.trials = []
        self.control = Control(.12, .5)

    def run(self):
        control = self.control
        for cv in range(0, 1000, 50):
            for cn in range(0, 1000, 50):
                control.reset()
                control.gold_getter.controversial(cv)
                control.gold_getter.consensus(cn)

                self.trials.append(Trial.from_control(cn, cv, control))

    def export(self, trials):
        data = [trial.plot() for trial in trials]
        distributions.multivar_scatter(data)


if __name__ == "__main__":
    x_ = range(50)
    y_ = range(50)
    z = lambda x, y: x + y

    data = []
    for x in x_:
        for y in y_:
            data.append((x, y, z(x, y)))

    print(data)
    distributions.multivar_scatter(None, data)

