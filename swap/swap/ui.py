################################################################

from swap.control import Control
import pickle
from pprint import pprint
import matplotlib.pyplot as plt
import argparse
import numpy as np
import os

from sklearn.metrics import roc_curve
from sklearn.metrics import auc


class Interface:

    def __init__(self):
        self.args = None
        self.dir = None

        self.p0 = 0.12
        self.epsilon = 0.5

        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()
        self.the_subparsers = {}

    def call(self):
        args = self.getArgs()

        self.option_dir(args)

        if args.p0:
            self.p0 = float(args.p0[0])

        if args.epsilon:
            self.epsilon = float(args.epsilon[0])

        args.func(args)

    def option_dir(self, args):
        if args.dir:
            _dir = args.dir[0]
            if not os.path.isdir(_dir):
                raise ValueError(
                    '%s Does not point to a valid directory' % _dir)

            if _dir[-1] == '/':
                _dir = _dir[:-1]

            self.dir = _dir

    def command_roc(self, args):
        if args.output:
            output = self.f(args.output[0])
        else:
            output = None

        data = self.collect_roc(args)

        title = 'Receiver Operater Characteristic'
        plot_roc(title, *data, fname=output)
        print(args)

    def save(self, object, fname):
        save_pickle(object, fname)

    def load(self, fname):
        return load_pickle(fname)

    def getArgs(self):
        if self.args is None:
            parser = self.options()
            args = parser.parse_args()
            self.args = args
            return args
        else:
            return self.args

    def options(self):
        parser = self.parser

        roc_parser = self.subparsers.add_parser('roc')
        roc_parser.set_defaults(func=self.command_roc)
        self.the_subparsers['roc'] = roc_parser

        # roc_parser.add_argument(
        #     'files', nargs='*',
        #     help='Pickle files used to generate roc curves')

        roc_parser.add_argument(
            '-a', '--add', nargs=2, action='append',
            help='Pickle files used to generate roc curves')

        roc_parser.add_argument(
            '--output', '-o', nargs=1,
            help='Write plot to file')

        parser.add_argument(
            '--dir', nargs=1,
            help='Direct all output to a different directory')

        parser.add_argument(
            '--p0', nargs=1,
            help='Define p0')

        parser.add_argument(
            '--epsilon', nargs=1,
            help='Define epsilon')

        return parser

    def f(self, fname):
        if fname == '-':
            return None
        if self.dir:
            return '%s/%s' % (self.dir, fname)
        else:
            return fname

    def collect_roc(self, args):
        data = []
        for label, fname in args.add:
            print(fname)
            obj = self.load(fname)
            data.append((label, obj.roc_export()))

            return data


class SWAPInterface(Interface):
    def __init__(self):
        super().__init__()

        self.control = None

    def options(self):
        parser = super().options()

        swap_parser = self.subparsers.add_parser('swap')
        swap_parser.set_defaults(func=self.command_swap)
        self.the_subparsers['swap'] = swap_parser

        swap_parser.add_argument(
            '--save', nargs=1,
            help='The filename where the SWAP object should be stored')

        swap_parser.add_argument(
            '--load', nargs=1,
            help='Load a pickled SWAP object')

        swap_parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        swap_parser.add_argument(
            '--subject', nargs=1,
            help='Generate subject track plot and output to filename S')

        swap_parser.add_argument(
            '--user', nargs=1,
            help='Generate user track plots and output to filename U')

        swap_parser.add_argument(
            '--log', nargs=1,
            help='Write the entire SWAP export to file')

        return parser

    def command_swap(self, args):
        swap = None

        if args.load:
            swap = self.load(args.load[0])

        if args.run:
            swap = self.run_swap()

        if args.save:
            self.save(swap, self.f(args.save[0]))

        if args.subject:
            fname = self.f(args.subject[0])
            plot_subjects(swap, fname)

        if args.user:
            fname = self.f(args.user[0])
            plot_users(swap, fname)

        if args.log:
            fname = self.f(args.output[0])
            write_log(swap, fname)

        return swap

    def _control(self):
        return Control(self.p0, self.epsilon)

    def getControl(self):
        if self.control is None:
            self.control = self._control()

        return self.control

    def run_swap(self, fname):
        control = self.getControl()
        control.process()
        swap = control.getSWAP()

        ui.save_pickle(swap, fname)

        return swap


def run(interface=None):
    if interface:
        interface.call()
    else:
        Interface().call()


def load_pickle(fname):
    with open(fname, 'rb') as file:
        data = pickle.load(file)
    return data


def save_pickle(object, fname):
    with open(fname, 'wb') as file:
        pickle.dump(object, file)


def plot_users(swap, fname):
    export = swap.export()
    data = []
    for item in export['users'].values():
        h0 = item['score_0_history']
        h1 = item['score_1_history']

        h = []
        for i, v0 in enumerate(h0):
            if len(h1) <= i:
                v1 = h1[-1]
            else:
                v1 = h1[i]
            h.append((v0 + v1) / 2)
        data.append((1, h))

    plot_tracks(data, 'User Combined Tracks', fname, scale='log')


# def plot_users(swap, fname):
#     export = swap.export()

#     def getData(data, n):
#         data = []
#         for item in export['users'].values():
#             h = item['score_%d_history' % n]
#             if len(h) > 7:
#                 if len(h) > 20:
#                     data.append((n, h[7:20]))
#                 else:
#                     data.append((n, h[7:]))
#         return data

#     def plotData(export, n, fname):
#         name = fname.split('.')
#         name[0] += '-%d' % n
#         name = '.'.join(name)
#         plot_tracks(
#             getData(export, n),
#             'User %d Tracks' % n,
#             name, scale='linear')

#     # plotData(export, 1, fname)
#     # plotData(export, 0, fname)
#     combine_user_scores(export, fname)


def plot_subjects(swap, fname):
    export = swap.export()
    print(fname)
    data = [(d['gold_label'], d['history'])
            for d in export['subjects'].values()]
    plot_tracks(data, 'Subject Tracks', fname)


def plot_tracks(data, title, fname, dpi=300, scale='log'):
    """ Plot subject tracks """
    cmap = ["#669D31", "#F00200", "#000000"]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    count = 0
    for gold, history in data:
        if count == 1000:
            break

        ax.plot(
            [0.01] + history,
            range(len(history) + 1),
            "-",
            color=cmap[gold],
            lw=1,
            alpha=0.1)

        count += 1

    plt.xlim(-0.01, 1.01)
    ax.set_yscale(scale)
    plt.gca().invert_yaxis()

    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.title(title)

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()


def plot_histogram(data, title, fname, dpi=300):
    # the histogram of the data
    n, bins, patches = plt.hist(
        data, 50, normed=1,
        facecolor='green', alpha=0.75)

    # add a 'best fit' line
    # y = mlab.normpdf( bins, mu, sigma)
    # l = plt.plot(bins, y, 'r--', linewidth=1)

    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    plt.axis([0, 1, 0, 10])
    plt.grid(True)

    plt.show()


def plot_roc(title, *datasets, fname=None, dpi=300):
    plt.figure(1)

    for label, data in datasets:
        y_true = []
        y_score = []

        for t in data:
            y_true.append(t[0])
            y_score.append(t[1])

        y_true = np.array(y_true)
        y_score = np.array(y_score)

        # Compute fpr, tpr, thresholds and roc auc
        fpr, tpr, thresholds = roc_curve(y_true, y_score)
        roc_auc = auc(y_true, y_score, True)
        # roc_auc = 0

        # Plot ROC curve
        plt.plot(fpr, tpr, label='%s (area = %0.3f)' % (label, roc_auc))

    plt.plot([0, 1], [0, 1], 'k--')  # random predictions curve
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate or (1 - Specifity)')
    plt.ylabel('True Positive Rate or (Sensitivity)')
    plt.title('Receiver Operating Characteristic for %s' % title)
    plt.legend(loc="lower right")

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()


def write_log(data, fname):
    with open(fname, 'w') as file:
        pprint(data, file)


if __name__ == "__main__":
    # run()
    pass
