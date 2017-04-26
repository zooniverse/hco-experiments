################################################################

from swap.control import Control
import pickle
from pprint import pprint
import matplotlib.pyplot as plt
import argparse
import numpy as np
import os

from swap.plots.traces import *
from swap.plots.distributions import *


class Interface:
    """
        Common CLI interface for repetitive operations
    """

    def __init__(self):
        """
            Initialize variables
        """
        self.args = None
        self.dir = None

        self.p0 = 0.12
        self.epsilon = 0.5

        self.parser = argparse.ArgumentParser()
        self.subparsers = self.parser.add_subparsers()
        self.the_subparsers = {}

    def options(self):
        """
            Add command line options

            dir: Save all output to a separate subdirectory
            -a|--add: Add an object to roc curve generation queue
            --output: Save roc curve to file
            --p0: Use custom value for p0
            --epsilon: Use custom value for epsilon
        """
        parser = self.parser

        roc_parser = self.subparsers.add_parser('roc')
        roc_parser.set_defaults(func=self.command_roc)
        self.the_subparsers['roc'] = roc_parser

        # roc_parser.add_argument(
        #     'files', nargs='*',
        #     help='Pickle files used to generate roc curves')

        roc_parser.add_argument(
            '-a', '--add', nargs=2, action='append',
            metavar=('label', 'file'),
            help='Add pickled SWAP object to roc curve')

        roc_parser.add_argument(
            '--output', '-o', nargs=1,
            metavar='file',
            help='Save plot to file')

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

    def call(self):
        """
            Execute arguments
        """
        args = self.getArgs()
        print(args)

        self.option_dir(args)

        if args.p0:
            self.p0 = float(args.p0[0])

        if args.epsilon:
            self.epsilon = float(args.epsilon[0])

        if 'func' in args:
            args.func(args)

    def option_dir(self, args):
        """
            Output all plots and pickle files ot a sub directory

            Args:
                args: command line arguments
        """
        if args.dir:
            _dir = args.dir[0]
            if not os.path.isdir(_dir):
                raise ValueError(
                    '%s Does not point to a valid directory' % _dir)

            if _dir[-1] == '/':
                _dir = _dir[:-1]

            self.dir = _dir

    def command_roc(self, args):
        """
            Generate a roc curve

            Args:
                args: command line arguments
        """
        if args.output:
            output = self.f(args.output[0])
        else:
            output = None

        data = self.collect_roc(args)

        title = 'Receiver Operater Characteristic'
        plot_roc(title, *data, fname=output)
        print(args)

    def save(self, object, fname):
        """
            Pickle and save an object

            Args:
                object
                fname
        """
        save_pickle(object, fname)

    def load(self, fname):
        """
            Load pickled object from file

            Args:
                fname
        """
        return load_pickle(fname)

    def getArgs(self):
        """
            Commmon method to get arguments and store them in
            instance variable
        """
        if self.args is None:
            parser = self.options()
            args = parser.parse_args()
            self.args = args
            return args
        else:
            return self.args

    def f(self, fname):
        """
            Ensure directory specified with --dir is in
            a filename

            Args:
                fname: filename to modify
        """
        if fname == '-':
            return None
        if self.dir:
            return '%s/%s' % (self.dir, fname)
        else:
            return fname

    def collect_roc(self, args):
        """
            Load objects for roc curve from file
            and prepare data for roc curve generation

            Args:
                args: command line arguments
        """
        it = Roc_Iterator()
        if args.add:
            for label, fname in args.add:
                print(fname)
                # obj = self.load(fname)
                # data.append((label, obj.roc_export()))
                it.addObject(label, fname, self.load)

        return it


class SWAPInterface(Interface):
    """
        Customized interface to add SWAP operations
    """

    def __init__(self):
        """
            Initialize variables
        """
        super().__init__()

        self.control = None

    def options(self):
        """
            Add command line options
        """
        parser = super().options()

        swap_parser = self.subparsers.add_parser('swap')
        swap_parser.set_defaults(func=self.command_swap)
        self.the_subparsers['swap'] = swap_parser

        swap_parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='The filename where the SWAP object should be stored')

        swap_parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='Load a pickled SWAP object')

        swap_parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        swap_parser.add_argument(
            '--subject', nargs=1,
            metavar='file',
            help='Generate subject track plot and output to file')

        swap_parser.add_argument(
            '--utraces', nargs=1,
            metavar='file',
            help='Generate user track plots and output to file')

        swap_parser.add_argument(
            '--user', nargs=1,
            metavar='file',
            help='Generate user confusion matrices and outname to file')

        swap_parser.add_argument(
            '--log', nargs=1,
            metavar='file',
            help='Write the entire SWAP export to file')

        swap_parser.add_argument(
            '--train', nargs=1,
            metavar='n',
            help='Run swap with a test/train split. Restricts sample size' +
                 ' of gold labels to \'n\'')

        swap_parser.add_argument(
            '--stats', action='store_true',
            help='Display run statistics')

        swap_parser.add_argument(
            '--dist', nargs=2,
            help='Show distribution plot')

        return parser

    def command_swap(self, args):
        """
            Execute SWAP operations

            Args:
                args: command line arguments
        """
        swap = None

        if args.load:
            swap = self.load(args.load[0])

        if args.run:
            swap = self.run_swap(args)

        if args.save:
            self.save(swap, self.f(args.save[0]))

        if args.subject:
            fname = self.f(args.subject[0])
            plot_subjects(swap, fname)

        if args.user:
            fname = self.f(args.user[0])
            plot_user_cm(swap, fname)

        if args.utraces:
            fname = self.f(args.user[0])
            plot_user_traces(swap, fname)

        if args.log:
            fname = self.f(args.output[0])
            write_log(swap, fname)

        if args.stats:
            print(swap.stats_str())

        if args.dist:
            data = [s.getScore() for s in swap.subjects]
            plot_probability_density(data, self.f(args.dist[0]), swap,
                                     cutoff=float(args.dist[1]))

        return swap

    def getControl(self, train=None):
        """
            Returns the Control instance
            Defines a Control instance if it doesn't exist yet
        """
        if train is None:
            return Control(self.p0, self.epsilon)
        else:
            return Control(self.p0, self.epsilon, train_size=train)

    def run_swap(self, args):
        """
            Have the Control process all classifications
        """
        if args.train:
            train = int(args.train[0])
        else:
            train = None

        control = self.getControl(train)
        control.process()
        swap = control.getSWAP()

        return swap


def run(interface=None):
    """
        Run the interface

        Args:
            interface: Custom interface subclass to use
    """
    if interface:
        interface.call()
    else:
        Interface().call()


def load_pickle(fname):
    """
        Loads a pickled object from file
    """
    with open(fname, 'rb') as file:
        data = pickle.load(file)
    return data


def save_pickle(object, fname):
    """
        Pickles and saves an object to file
    """
    with open(fname, 'wb') as file:
        pickle.dump(object, file)


def plot_user_cm(swap, fname):
    data = []
    for user in swap.users:
        score0 = user.getScore(0)
        score1 = user.getScore(1)
        n = user.getCount()

        data.append((score0, score1, n))

    plot_confusion_matrix(data, "User Confusion Matrices", fname)


def plot_histogram(data, title, fname, dpi=300):
    """
        Generate a histogram plot
    """
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
        roc_auc = auc(fpr, tpr, True)
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


def plot_confusion_matrix(data, title, fname, dpi=300):
    # """ Plot User Skill """
    # # Loop over all users
    # user_data = swappy.exportUserData()
    # # all users
    # unique_users = user_data.keys()
    # # max classifications
    # max_class = 0
    # # number of user processed
    # counter = 0
    # for user in unique_users:
    #     n_class_user = len(user_data[user]['gold_labels'])
    #     max_class = max(max_class, n_class_user)
    #     plt.plot(user_data[user]['score_1_history'][-1],
    #              user_data[user]['score_0_history'][-1], "o",
    #              ms=(n_class_user)/500,
    #              color="#3F88C5", alpha=0.5)

    for item in data:
        plt.plot(item[1], item[0],
                 'o', ms=item[2] / 500,
                 color="#3F88C5", alpha=0.5)

    # Quadrant labels
    plt.text(0.03, 0.03, "Obtuse")
    plt.text(0.75, 0.03, "Optimistic")
    plt.text(0.03, 0.95, "Pessimistic")
    plt.text(0.8, 0.95, "Astute")

    # Quadrant divider lines
    plt.plot([0.5, 0.5], [0, 1], "k--", lw=1)
    plt.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    plt.plot([0, 1], [1, 0], "k-", lw=1)

    # Axis labels
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')

    # Plot Title
    plt.title(title)

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()


class Roc_Iterator:
    def __init__(self):
        self.items = []
        self.i = 0

    def addObject(self, label, fname, load):
        self.items.append((label, fname, load))

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __bounds(self):
        if self.i >= len(self.items):
            raise StopIteration()

    def next(self):
        self.__bounds()
        if self.i > len(self.items):
            raise StopIteration()

        label, fname, load = self.items[self.i]

        obj = load(fname)
        self.i += 1

        return (label, obj.roc_export())


def write_log(data, fname):
    with open(fname, 'w') as file:
        pprint(data, file)


if __name__ == "__main__":
    # run()
    pass
