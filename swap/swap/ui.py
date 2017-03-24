################################################################

from swap.control import Control
import pickle
from pprint import pprint
import matplotlib.pyplot as plt
import argparse


class Interface:

    def __init__(self):
        self.args = None
        self.control = None

    def call(self):
        args = self.getArgs()

        if args.p:
            data = run_swap(self.getControl(), args.pickle)
        else:
            data = load_pickle(args.pickle)

        if args.s:
            plot_subjects(data, args.s[0])

        if args.u:
            plot_users(data, args.u[0])

        if args.output:
            write_output(data, args.output[0])

        return data

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


def run(interface=Interface):
    interface.call()


def load_pickle(fname):
    with open(fname, 'rb') as file:
        data = pickle.load(file)
    return data


def run_swap(control, fname):
    control.process()

    data = control.getSWAP().export()
    # with open('log', 'w') as file:
    #     yaml.dump(data, file)

    with open(fname, 'wb') as file:
        pickle.dump(data, file)

    return data


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


def combine_user_scores(export, fname):
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

    plot_tracks(data, 'User Combined Tracks', name, scale='linear')


def plot_users(export, fname):
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

    plotData(export, 1, fname)
    plotData(export, 0, fname)
    combine_user_scores(export, fname)


def plot_subjects(export, fname):
    print(fname)
    data = [(d['gold_label'], d['history'])
            for d in export['subjects'].values()]
    plot_tracks(data, 'Subject Tracks', fname)


def plot_tracks(data, title, fname, dpi=600, scale='log'):
    """ Plot subject tracks """
    cmap = ["#669D31", "#F00200"]

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
            alpha=0.2)

        count += 1

    plt.xlim(-0.01, 1.01)
    ax.set_yscale(scale)
    plt.gca().invert_yaxis()

    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.title(title)

    plt.savefig(fname, dpi=dpi)
    # plt.show()


def write_output(data, fname):
    with open(fname, 'w') as file:
        pprint(data, file)


if __name__ == "__main__":
    # run()
    pass
