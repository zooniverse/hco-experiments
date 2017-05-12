

class ExperimentRun:
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


class Experiment:
    pass
