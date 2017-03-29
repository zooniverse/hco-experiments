################################################################

from swap.control import Control
import pickle
from pprint import pprint
import matplotlib.pyplot as plt
import argparse
import numpy as np

from sklearn.metrics import roc_curve
from sklearn.metrics import auc


class Interface:

    def __init__(self):
        self.args = None
        self.control = None

    def call(self):
        args = self.getArgs()

        if args.pickle != '-':
            if args.p:
                swap = run_swap(self.getControl(), args.pickle)
            else:
                swap = load_pickle(args.pickle)

            if args.s:
                plot_subjects(swap, args.s[0])

            if args.u:
                plot_users(swap, args.u[0])

            if args.output:
                write_output(swap, args.output[0])

            return swap

    def getControl(self):
        if self.control is None:
            self.control = self._control()

        return self.control

    def _control(self):
        return Control(.01, .5)

    def getArgs(self):
        if self.args is None:
            parser = self.options()
            args = parser.parse_args()
            self.args = args
            return args
        else:
            return self.args

    def options(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-p', action='store_true',
            help='Run the SWAP algorithm again, and pickle and save')
        parser.add_argument(
            'pickle', help='The filename of the pickled SWAP export')
        parser.add_argument(
            '-s', nargs=1,
            help='Generate subject track plot and output to filename S')
        parser.add_argument(
            '-u', nargs=1,
            help='Generate user track plots and output to filename U')
        parser.add_argument(
            '--output', nargs=1,
            help='Not instantiated yet')

        return parser


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


def run_swap(control, fname):
    control.process()
    swap = control.getSWAP()

    save_pickle(swap, fname)

    return swap


def find_errors():
    with open('pickle.pkl', 'rb') as file:
        data = pickle.load(file)

    interest = []
    for key, value in data['subjects'].items():
        if 1.0 in value['history'] or 0 in value['history']:
            interest.append(value)

    print(len(interest))
    plot_subjects(data,
                  "Subject Tracks",
                  "subject_tracks.png")

    with open('log', 'w') as file:
        pprint(interest, file)


def combine_user_scores(swap, fname):
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

    name = fname.split('.')
    name[0] += '-combined'
    name = '.'.join(name)

    plot_tracks(data, 'User Combined Tracks', name, scale='log')


def plot_users(swap, fname):
    export = swap.export()
    def getData(data, n):
        data = []
        for item in export['users'].values():
            h = item['score_%d_history' % n]
            if len(h) > 7:
                if len(h) > 20:
                    data.append((n, h[7:20]))
                else:
                    data.append((n, h[7:]))
        return data

    def plotData(export, n, fname):
        name = fname.split('.')
        name[0] += '-%d' % n
        name = '.'.join(name)
        plot_tracks(
            getData(export, n),
            'User %d Tracks' % n,
            name, scale='linear')

    # plotData(export, 1, fname)
    # plotData(export, 0, fname)
    combine_user_scores(export, fname)


def plot_subjects(swap, fname):
    export = swap.export()
    print(fname)
    data = [(d['gold_label'], d['history'])
            for d in export['subjects'].values()]
    plot_tracks(data, 'Subject Tracks', fname)


def plot_tracks(data, title, fname, dpi=600, scale='log'):
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

    plt.savefig(fname, dpi=dpi)
    # plt.show()


def plot_histogram(data, title, fname, dpi=600):
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


def plot_roc(datasets, title, fname, dpi=600):
    plt.figure()

    # TODO better way to receive multiple datasets
    if type(datasets) not in [list, tuple]:
        datasets = (datasets)

    for data in datasets:
        y_true = []
        y_score = []

        for i, t in enumerate(data):
            y_true.append(t[0])
            y_score.append(t[1])

        y_true = np.array(y_true)
        y_score = np.array(y_score)

        # Compute fpr, tpr, thresholds and roc auc
        fpr, tpr, thresholds = roc_curve(y_true, y_score)
        roc_auc = auc(y_true, y_score, True)
        # roc_auc = 0

        # Plot ROC curve
        plt.plot(fpr, tpr, label='ROC curve (area = %0.3f)' % roc_auc)

    plt.plot([0, 1], [0, 1], 'k--')  # random predictions curve
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate or (1 - Specifity)')
    plt.ylabel('True Positive Rate or (Sensitivity)')
    plt.title('Receiver Operating Characteristic for %s' % title)
    plt.legend(loc="lower right")

    # plt.show()
    plt.savefig(fname, dpi=dpi)


def write_output(data, fname):
    with open(fname, 'w') as file:
        pprint(data, file)


if __name__ == "__main__":
    # run()
    pass
