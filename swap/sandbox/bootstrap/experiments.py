
import swap.plots.distributions as distributions
from swap import Control
from swap.agents.agent import Stat
import swap.db.experiment as dbe


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

    def purity(self, cutoff):
        return self.scores.purity(cutoff)

    def purify(self):
        pass

    def plot(self, cutoff):
        return (self.consensus, self.controversial, self.purity(cutoff))

    @staticmethod
    def from_control(consensus, controversial, control):
        t = Trial(consensus, controversial,
                  control.gold_getter.golds,
                  control.getSWAP().score_export())
        return t

    def db_export(self):
        export = {}
        export['consensus'] = self.consensus
        export['controversial'] = self.controversial

        golds = {'0': [], '1': [], '-1': []}
        for id_, gold in self.golds.items():
            golds[str(gold)].append(id_)
        export['golds'] = golds

        def score_to_bson(score):
            subject, gold, p = score
            return {'subject': subject, 'gold': gold, 'score': p}

        export['scores'] = [score_to_bson(x) for x in self.scores.full()]

        return export


class Experiment:
    def __init__(self, saver, cutoff=0.96):
        self.trials = []
        self.plot_points = []
        self.control = Control(.12, .5)
        self.save_f = saver
        self.p_cutoff = cutoff

    @staticmethod
    def from_trial_export(directory, cutoff, saver, loader):
        files = get_trials(directory)

        e = Experiment(saver, cutoff)
        for fname in files:
            print(fname)
            trials = loader(fname)
            for trial in trials:
                e.add_trial(trial)
            e.trials = []

        return e

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
                self.add_trial(Trial.from_control(cn, cv, control))

                n += 1
            self.clear_mem(cv, cn)

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
        self.trials = []

    def add_trial(self, trial):
        self.trials.append(trial)
        self.plot_points.append(trial.plot(self.p_cutoff))

    def plot(self, fname):
        data = self.plot_points
        distributions.multivar_scatter(fname, data)

    def __str__(self):
        s = '%d points\n' % len(self.plot_points)
        s += str(Stat([i[2] for i in self.plot_points]))
        return s

    def __repr__(self):
        return str(self)


def upload_trials(directory, loader):
    files = get_trials(directory)
    for fname in files:
        print(fname)
        trials = loader(fname)
        dbe.upload_trials(trials)

        break


def get_trials(directory):
    import os
    import re

    pattern = re.compile('trials_cv_[0-9]{1,4}_cn_[0-9]{1,4}.pkl')

    def _path(fname):
        return os.path.join(directory, fname)

    def istrial(fname):
        if pattern.match(fname):
            return True
        else:
            return False

    files = []
    for fname in os.listdir(directory):
        path = _path(fname)
        if os.path.isfile(path) and istrial(fname):
            files.append(path)

    return files


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
