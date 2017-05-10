################################################################

from swap.control import Control
import pickle
from pprint import pprint
import argparse
import os

import swap.plots as plots


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
        plots.plot_roc(title, *data, fname=output)
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
            '--hist', nargs=1,
            metavar='file',
            help='Generate multiclass histogram plot')

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
            '--controversial', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'controversial subjects')

        swap_parser.add_argument(
            '--consensus', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'consensus subjects')

        # swap_parser.add_argument(
        #     '--extremes', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        # swap_parser.add_argument(
        #     '--extreme-min', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        swap_parser.add_argument(
            '--stats', action='store_true',
            help='Display run statistics')

        swap_parser.add_argument(
            '--dist', nargs=2,
            help='Show distribution plot')

        swap_parser.add_argument(
            '--diff', nargs='*',
            help='Visualize performance difference between swap outputs')

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
            plots.traces.plot_subjects(swap, fname)

        if args.user:
            fname = self.f(args.user[0])
            plots.plot_user_cm(swap, fname)

        if args.hist:
            fname = self.f(args.hist[0])
            plots.plot_class_histogram(fname, swap)

        if args.utraces:
            fname = self.f(args.user[0])
            plots.traces.plot_user(swap, fname)

        if args.log:
            fname = self.f(args.output[0])
            write_log(swap, fname)

        if args.stats:
            print(swap.stats_str())

        if args.dist:
            data = [s.getScore() for s in swap.subjects]
            plots.plot_pdf(data, self.f(args.dist[0]), swap,
                           cutoff=float(args.dist[1]))

        if args.diff:
            self.difference(args)

        return swap

    def getControl(self):
        """
            Returns the Control instance
            Defines a Control instance if it doesn't exist yet
        """
        control = Control(self.p0, self.epsilon)

        return control

    def run_swap(self, args):
        """
            Have the Control process all classifications
        """
        control = self.getControl()

        # Random test/train split
        if args.train:
            train = int(args.train[0])
            control.gold_getter.random(train)

        if args.controversial:
            size = int(args.controversial[0])
            control.gold_getter.controversial(size)

        if args.consensus:
            size = int(args.consensus[0])
            control.gold_getter.consensus(size)

        # if args.extremes:
        #     controversial = int(args.extremes[0])
        #     consensus = int(args.extremes[1])
        #     control.gold_getter.extremes(controversial, consensus)

        # if args.extreme_min:
        #     controversial = int(args.extreme_min[0])
        #     consensus = int(args.extreme_min[1])
        #     control.gold_getter.extreme_min(controversial, consensus)

        control.process()
        swap = control.getSWAP()

        return swap

    def difference(self, args):
        base = load_pickle(args.diff[0])
        fname = self.f(args.diff[-1])

        items = args.diff[1:-1]
        items = [tuple(items[i: i + 2]) for i in range(0, len(items), 2)]
        print(items)

        # other = [load_pickle(x) for x in args.diff[1:]]
        plots.performance.p_diff(base, items, fname, self.load)


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
    try:
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        return data
    except Exception as e:
        print('Error load file %s' % fname)
        raise e


def save_pickle(object, fname):
    """
        Pickles and saves an object to file
    """
    with open(fname, 'wb') as file:
        pickle.dump(object, file)


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

    def _get_export(self, obj):
        return obj.roc_export()

    def next(self):
        self.__bounds()
        if self.i > len(self.items):
            raise StopIteration()

        label, fname, load = self.items[self.i]

        obj = load(fname)
        self.i += 1

        return (label, self._get_export(obj))


def write_log(data, fname):
    with open(fname, 'w') as file:
        pprint(data, file)


if __name__ == "__main__":
    # run()
    pass
