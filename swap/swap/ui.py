################################################################

from swap.control import Control
from swap.config import Config
import swap.plots as plots

from swap.utils import ScoreExport
from swap.swap import SWAP

import pickle
from pprint import pprint
import argparse
import os
import sys


class UI:
    def __init__(self):
        self.interfaces = {}
        self.parser = argparse.ArgumentParser()
        self.sparsers = self.parser.add_subparsers()

        self.dir = None

        self.options(self.parser)

    def run(self):
        args = self.parser.parse_args()
        print(args)
        self.call(args)

    def options(self, parser):
        parser.add_argument(
            '--dir', nargs=1,
            help='Direct all output to a different directory')

        parser.add_argument(
            '--p0', nargs=1,
            help='Define p0')

        parser.add_argument(
            '--epsilon', nargs=1,
            help='Define epsilon')

        parser.add_argument(
            '--pow', action='store_true',
            help='controversial and consensus aggregation method')

        parser.add_argument(
            '--multiply', action='store_true',
            help='controversial and consensus aggregation method')

    def call(self, args):
        """
            Execute arguments
        """
        config = Config()

        if args.dir:
            self.set_dir(args.dir[0])

        if args.p0:
            config.p0 = float(args.p0[0])

        if args.epsilon:
            config.epsilon = float(args.epsilon[0])

        if args.pow:
            config.controversial_version = 'pow'
        elif args.multiply:
            config.controversial_version = 'multiply'

        if 'func' in args:
            args.func(args)

    def add(self, interface):
        command = interface.command

        sparser = self.sparsers.add_parser(command)
        sparser.set_defaults(func=interface.call)

        interface.options(sparser)
        self.interfaces[command] = interface

    @property
    def args(self):
        pass

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
            return os.path.join(self.dir, fname)
        else:
            return fname

    def set_dir(self, dir_):
        """
            Output all plots and pickle files ot a sub directory

            Args:
                args: command line arguments
        """
        if not os.path.isdir(dir_):
            raise ValueError(
                '%s Does not point to a valid directory' % dir_)

        if dir_[-1] == '/':
            dir_ = dir_[:-1]

        self.dir = dir_


class Interface:

    def __init__(self, ui):
        self.ui = ui
        ui.add(self)
        self.init()

    def init(self):
        pass

    @property
    def command(self):
        pass

    def options(self, parser):
        pass

    def call(self, args):
        pass

    ###############################################################

    def save(self, object, fname):
        """
            Pickle and save an object

            Args:
                object
                fname
        """
        if fname is not None:
            save_pickle(object, fname)

    def load(self, fname):
        """
            Load pickled object from file

            Args:
                fname
        """
        return load_pickle(fname)

    def f(self, fname):
        return self.ui.f(fname)


class RocInterface(Interface):

    @property
    def command(self):
        return 'roc'

    def options(self, parser):

        # roc_parser.add_argument(
        #     'files', nargs='*',
        #     help='Pickle files used to generate roc curves')

        parser.add_argument(
            '-a', '--add', nargs=2, action='append',
            metavar=('label', 'file'),
            help='Add pickled SWAP object to roc curve')

        parser.add_argument(
            '--output', '-o', nargs=1,
            metavar='file',
            help='Save plot to file')

    def call(self, args):
        """
            Generate a roc curve

            Args:
                args: command line arguments
        """
        super().call(args)

        if args.output:
            output = self.f(args.output[0])
        else:
            output = None

        iterator = self.collect_roc(args)

        title = 'Receiver Operater Characteristic'
        plots.plot_roc(title, iterator, fname=output)
        print(args)

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
                it.addObject(label, fname, self.load)

        return it


################################################################
#
# SWAP
#
################################################################


class SWAPInterface(Interface):
    """
        Customized interface to add SWAP operations
    """

    def init(self):
        """
            Initialize variables
        """
        self.control = None

    @property
    def command(self):
        return 'swap'

    def options(self, parser):

        parser.add_argument(
            '--save', nargs=1,
            metavar='file',
            help='save swap to file')

        parser.add_argument(
            '--save-scores', nargs=1,
            metavar='file',
            help='save swap scores to file')

        parser.add_argument(
            '--load', nargs=1,
            metavar='file',
            help='Load a pickled SWAP object')

        parser.add_argument(
            '--run', action='store_true',
            help='Run the SWAP algorithm')

        parser.add_argument(
            '--subject', nargs=1,
            metavar='file',
            help='Generate subject track plot and output to file')

        parser.add_argument(
            '--utraces', nargs=1,
            metavar='file',
            help='Generate user track plots and output to file')

        parser.add_argument(
            '--user', nargs=1,
            metavar='file',
            help='Generate user confusion matrices and outname to file')

        parser.add_argument(
            '--hist', nargs=1,
            metavar='file',
            help='Generate multiclass histogram plot')

        parser.add_argument(
            '--scores', nargs=1,
            metavar='file',
            help='Save swap scores to file')

        parser.add_argument(
            '--log', nargs=1,
            metavar='file',
            help='Write the entire SWAP export to file')

        parser.add_argument(
            '--train', nargs=1,
            metavar='n',
            help='Run swap with a test/train split. Restricts sample size' +
                 ' of gold labels to \'n\'')

        parser.add_argument(
            '--controversial', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'controversial subjects')

        parser.add_argument(
            '--consensus', nargs=1,
            metavar='n',
            help='Run swap with a test/train split, using the most/least' +
                 'consensus subjects')

        # parser.add_argument(
        #     '--extremes', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        # parser.add_argument(
        #     '--extreme-min', nargs=2,
        #     metavar='controversial consensus',
        #     help='Run swap with a test/train split, using the most' +
        #          'controversial subjects and subjects with most consensus')

        parser.add_argument(
            '--stats', action='store_true',
            help='Display run statistics')

        parser.add_argument(
            '--dist', nargs=2,
            help='Show distribution plot')

        parser.add_argument(
            '--diff', nargs='*',
            help='Visualize performance difference between swap outputs')

        parser.add_argument(
            '--shell', action='store_true')

        parser.add_argument(
            '--test', action='store_true')

    def call(self, args):
        swap = None

        if args.load:
            swap = self.load(args.load[0])

        if args.run:
            swap = self.run_swap(args)

        if args.save:
            manifest = self.manifest(swap, args)
            self.save(swap, self.f(args.save[0]), manifest)

        if args.save_scores:
            fname = self.f(args.save_scores[0])
            self.save_scores(swap, fname)

        if args.subject:
            fname = self.f(args.subject[0])
            plots.traces.plot_subjects(swap, fname)

        if args.user:
            fname = self.f(args.user[0])
            plots.plot_user_cm(swap, fname)

        if args.hist:
            fname = self.f(args.hist[0])
            plots.plot_class_histogram(fname, swap.score_export())

        if args.utraces:
            fname = self.f(args.user[0])
            plots.traces.plot_user(swap, fname)

        if args.log:
            fname = self.f(args.log[0])
            write_log(swap, fname)

        if args.scores:
            fname = self.f(args.scores[0])
            self.save(swap.score_export(), fname)

        if args.stats:
            print(swap.stats_str())

        if args.dist:
            data = [s.getScore() for s in swap.subjects]
            plots.plot_pdf(data, self.f(args.dist[0]), swap,
                           cutoff=float(args.dist[1]))

        if args.diff:
            self.difference(args)

        if args.test:
            from swap.control import GoldGetter
            gg = GoldGetter()
            print('applying new gold labels')
            swap.set_gold_labels(gg.golds)
            swap.process_changes()

        if args.shell:
            import code
            from swap import ui
            assert ui

            def save_scores(fname):
                self.save(swap.score_export(), self.f(fname))

            code.interact(local=locals())

        return swap

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

        control.run()
        swap = control.getSWAP()

        return swap

    def save_scores(self, swap, fname):
        self.save(swap.score_export(), fname)

    def manifest(self, swap, args):
        def arg_str(args):
            s = ''
            for key, value in args._get_kwargs():
                if key in ['func']:
                    continue
                s += '%13s  %s\n' % (key, value)

            return s

        s = swap.manifest() + '\n'
        s += 'UI Manifest\n'
        s += '===========\n'
        s += 'args:\n%s' % arg_str(args)

        return s

    def save(self, obj, fname, manifest=None):
        if manifest != '' and manifest is not None:
            m_fname = fname.split('.')
            m_fname = m_fname[:-1]
            m_fname[-1] += '-manifest'
            m_fname = '.'.join(m_fname)
            with open(self.f(m_fname), 'w') as file:
                file.write(manifest)

        super().save(obj, fname)

    def getControl(self):
        """
            Returns the Control instance
            Defines a Control instance if it doesn't exist yet
        """
        control = Control()

        return control

    def difference(self, args):
        base = load_pickle(args.diff[0])
        fname = self.f(args.diff[-1])

        items = args.diff[1:-1]
        items = [tuple(items[i: i + 2]) for i in range(0, len(items), 2)]
        print(items)

        # other = [load_pickle(x) for x in args.diff[1:]]
        plots.performance.p_diff(base, items, fname, self.load)


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
    sys.setrecursionlimit(10000)
    with open(fname, 'wb') as file:
        pickle.dump(object, file)


def run(*interfaces):
    """
        Run the interface

        Args:
            interface: Custom interface subclass to use
    """
    ui = UI()
    RocInterface(ui)
    SWAPInterface(ui)
    for interface in interfaces:
        interface()

    ui.run()


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
        if isinstance(obj, ScoreExport):
            return obj.roc()
        elif isinstance(obj, SWAP):
            return obj.score_export().roc()
        else:
            raise TypeError(
                'Did not recognize valid type for roc iterator %s' % type(obj))

    def next(self):
        self.__bounds()
        if self.i > len(self.items):
            raise StopIteration()

        label, fname, load = self.items[self.i]

        obj = load(fname)
        self.i += 1

        return (label, self._get_export(obj))


def write_log(swap, fname):
    with open(fname, 'w') as file:
        file.writelines(swap.debug_str())


if __name__ == "__main__":
    # run()
    pass
