#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels
from swaptools.bootstrap import Bootstrap
import swaptools.experiments.cv_grid_experiment as cv_experiment
import swaptools.experiments.random_golds as random_experiment
import swaptools.experiments.ordered_golds as ordered_golds

import swap.ui
import swap.plots as plots

import logging
logger = logging.getLogger(__name__)


class BootInterface(swap.ui.Interface):

    def init(self):

        self.last_load = None

    @property
    def command(self):
        return 'boot'

    def options(self, parser):
        # parser.add_argument(
        #     '--threshold', nargs=2,
        #     help='Print the number of subjects above or below the threshold')

        parser.add_argument(
            '--iterate', nargs=3,
            help='Iterate SWAP N times with the ' +
                 'specified (low, high) thresholds')

        parser.add_argument(
            '--thresholds', '-t', nargs=3)

        parser.add_argument(
            '--traces', nargs=1,
            metavar='file',
            help='Generate trace plot of bootstrap iterations')

        parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='load a pickled bootstrap from file')

        parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='load a pickled bootstrap from file')

        parser.add_argument(
            '--histogram', nargs=1,
            metavar='file',
            help='Draw a histogram of bootstrap data')

        parser.add_argument(
            '--cm', nargs=3)

        parser.add_argument(
            '--utraces', nargs='*')

    def call(self, args):
        if args.load:
            bootstrap = self.load(args.load[0])
        else:
            bootstrap = None

        if args.iterate:
            bootstrap = self.iterate(args)

        if args.traces and bootstrap:
            fname = self.f(args.traces[0])
            self.plot_bootstrap(bootstrap, fname)

        if args.cm and bootstrap:
            if len(args.cm) < 2:
                raise ValueError('Must specify at least one swap level')
            self.confusion_matrix_err(bootstrap, args)

        if args.utraces and bootstrap:
            if len(args.cm) < 2:
                raise ValueError('Must specify at least one swap level')
            self.user_traces(bootstrap, args)

        if args.save:
            fname = self.f(args.save[0])
            self.save(bootstrap, fname)

    def save(self, obj, fname):
        if isinstance(obj, Bootstrap):
            with open(self.f('manifest'), 'w') as file:
                file.write(obj.manifest())

        super().save(obj, fname)

    def load(self, fname):
        return load(fname)

    def mod_f(self, fname, append):
        append = str(append)

        f = fname[:]
        i = f.find('.')
        f = f[:i] + '-%s' % append + f[i:]

        return self.f(f)

    ################################################################
    #
    # Bootstrap
    #
    ################################################################

    def threshold(self, data, threshold):
        min = float(threshold[0])
        max = float(threshold[1])
        high = 0
        low = 0
        other = 0

        for subject, item in data['subjects'].items():
            if item['score'] < min:
                low += 1
            elif item['score'] > max:
                high += 1
            else:
                other += 1

        print('high: %d, low: %d, other: %d' % (high, low, other))

    def iterate(self, args):
        if args.save:
            fname = args.save[0]
        else:
            fname = None

        n = int(args.iterate[0])
        low = float(args.iterate[1])
        high = float(args.iterate[2])

        # TODO doesn't work
        thresholds = {}
        if args.thresholds:
            i = int(args.thresholds[0]) - 1
            low = float(args.thresholds[1])
            high = float(args.thresholds[2])
            thresholds[i] = (low, high)

        bootstrap = Bootstrap(low, high)

        for i in range(n):
            if i in thresholds:
                bootstrap.setThreshold(*thresholds[i])

            swap = bootstrap.step()
            if fname:
                self.save(swap,
                          self.mod_f(fname, 'swap-%d' % i))

            img = self.f('iterate-%d.png' % i)
            plots.traces.plot_subjects(swap, img)

        # if fname:
        #     self.save(bootstrap, fname)

        return bootstrap

    def confusion_matrix_err(self, bootstrap, args):
        level = int(args.cm[0]) - 1
        swap_name = args.cm[1]
        fname = self.f(args.cm[2])

        swap = self.load(swap_name)
        bswap = bootstrap.getMetric(level).getSWAP()

        data = []
        for id_ in swap.users.idset():

            a_user = swap.users.get(id_)
            b_user = bswap.users.get(id_)

            error = [0, 0]
            for i in [0, 1]:
                a = a_user.getScore(i)
                b = b_user.getScore(i)
                error[i] = a - b / a

            data.append((*error, 10))

        plots.plot_confusion_matrix(data, "Test", None)

    def user_traces(self, bootstrap, args):
        pass

    def plot_bootstrap(self, bootstrap, fname):
        plot_data = []
        for subject, value in bootstrap.export().items():
            if subject in bootstrap.silver:
                c = bootstrap.silver[subject]
            else:
                c = 2

            history = value['history']
            plot_data.append((c, history))

        plots.traces.plot_tracks(plot_data, "Bootstrap Traces",
                                 fname, scale='linear')


################################################################
#
# Experiment
#
################################################################


# class ExperimentInterface(swap.ui.Interface):

#     @property
#     def command(self):
#         return 'experiment'

#     def options(self, parser):

#         parser.add_argument(
#             '--run', nargs=2,
#             metavar=('trials directory, experiment file'))

#         parser.add_argument(
#             '--pow', action='store_true',
#             help='controversial and consensus aggregation method')

#         parser.add_argument(
#             '--multiply', action='store_true',
#             help='controversial and consensus aggregation method')

#         parser.add_argument(
#             '--cutoff', nargs=1,
#             help='p cutoff')

#         parser.add_argument(
#             '--from-trials', nargs=1,
#             metavar='directory with trial files',
#             help='load experiment plot data from trial files')

#         parser.add_argument(
#             '--load', nargs=1,
#             metavar='file',
#             help='load pickled experiment data')

#         parser.add_argument(
#             '--save', nargs=1,
#             metavar='file',
#             help='pickle and save experiment data')

#         parser.add_argument(
#             '--plot', nargs=2,
#             metavar=('type', 'file'),
#             help='Generate experiment plot')

#         parser.add_argument(
#             '--shell', action='store_true',
#             help='Drop to python interpreter after loading experiment')

#         parser.add_argument(
#             '--upload', nargs=1,
#             metavar='directory containing trial files',
#             help='Upload trials to mongo database')

#     def call(self, args):
#         if args.cutoff:
#             cutoff = float(args.cutoff[0])
#         else:
#             cutoff = 0.96

#         if args.pow:
#             Config().controversial_version = 'pow'
#         elif args.multiply:
#             Config().controversial_version = 'multiply'

#         if args.run:
#             d_trials = self.f(args.run[0])
#             f_pickle = self.f(args.run[1])

#             def saver(trials, fname):
#                 fname = os.path.join(d_trials, fname)
#                 self.save(trials, fname)
#             e = Experiment(saver)
#             e.run()

#             del e.save_f
#             self.save(e, f_pickle)

#         elif args.from_trials:
#             e = Experiment.from_trial_export(
#                 args.from_trials[0],
#                 cutoff, self.save, self.load)

#         elif args.load:
#             e = self.load(args.load[0])

#         if args.plot:
#             assert e
#             fname = self.f(args.plot[1])
#             type_ = args.plot[0]

#             if type_ == 'purity':
#                 e.plot_purity(fname)
#             elif type_ == 'completeness':
#                 e.plot_completeness(fname)
#             elif type_ == 'both':
#                 e.plot_both(fname)

#         if args.shell:
#             import code
#             code.interact(local=locals())

#         if args.save:
#             assert e
#             del e.save_f
#             self.save(e, self.f(args.save[0]))

#         if args.upload:
#             ex.upload_trials(args.upload[0], self.load)


################################################################
#
# ROC
#
################################################################


class RocInterface(swap.ui.RocInterface):

    def call(self, args):
        pass

    def options(self, parser):
        super().options(parser)

        parser.add_argument(
            '-b', '--bootstrap', nargs='*', action='append',
            help='Generate ROC curve from this file, bootstrap specific')

        parser.add_argument(
            '-s', '--silver-only', nargs=2,
            help='Generate roc curves only considering the silver ' +
                 'subjects in this file and round')

    def collect_roc(self, args):
        it = super().collect_roc(args)
        it.__class__ = Roc_Iterator

        if args.silver_only:
            print("Silver only:")
            silver_fname = args.silver_only[0]
            silver_round = int(args.silver_only[1])
            silvers = self.get_silvers(silver_fname, silver_round)

            it.silver_only(silvers)

        if args.bootstrap:
            for label, fname, *steps in args.bootstrap:
                print(fname)
                steps = [int(i) - 1 for i in steps]
                it.addBootObject(label, fname, self.load, steps)

        return it

    def get_silvers(self, fname, round_):
        boot = self.load(fname)
        silvers = boot.metrics.get(round_).getSilverNames()
        return silvers

    def load(self, fname):
        return load(fname)


class Roc_Iterator(swap.ui.Roc_Iterator):

    def addBootObject(self, label, fname, load,
                      iterations=None, silver_only=False):
        if iterations:
            self.items.append((label, fname, load, iterations, silver_only))

    def silver_only(self, silver_labels):
        self.silvers = silver_labels

    def _get_export(self, obj, *args, **kwargs):
        if isinstance(obj, Bootstrap):
            return obj.roc_export(*args, labels=self.silvers, **kwargs)
        else:
            return obj.score_export().roc(labels=self.silvers)

    def next(self):
        self.__bounds()

        item = self.items[self.i]
        if len(item) < 4:
            return super().next()
        elif len(item[3]) == 0:
            self.i += 1
            return self.next()
        else:
            print(item)
            label, fname, load = item[:3]
            i = item[3].pop(0)
            label = '%s-%d' % (label, i + 1)

            obj = load(fname)

            return (label, self._get_export(obj, i))


def load(self, fname):
    if self.last_load is not None and \
            self.last_load[0] == fname:
        return self.last_load[1]
    else:
        self.last_load = None

        obj = super().load(fname)
        self.last_load = (fname, obj)

        return obj


def run():
    ui = swap.ui.UI()
    RocInterface(ui)
    BootInterface(ui)
    cv_experiment.Interface(ui)
    random_experiment.Interface(ui)
    ordered_golds.Interface(ui)

    ui.run()
