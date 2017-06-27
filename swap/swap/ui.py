################################################################

from swap.control import Control
import swap.config as config
import swap.plots as plots
import swap.app.caesar_app as caesar

from swap.utils.scores import ScoreExport
from swap.swap import SWAP

import pickle
import argparse
import os
import sys
import csv

import logging
logger = logging.getLogger(__name__)

__doc__ = """
    An interface to interact with our utilities from the command line.
    Makes it easier to repeated run SWAP under different conditions.

    UI:
        Container for all the different interfaces

    Interface:
        A construct that manages options and determines the right action

    SWAPInterface:
        An interface for interacting with SWAP

    RocInterface:
        An interface to generate roc curves from multiple SWAP exports
"""
__author__ = "Michael Laraia"


class UI:
    """
    Main interface endpoint, manages interaction with argparse. Interfaces
    register with a UI instance, and the UI instance chooses the right
    Interface to pass args to.
    """

    def __init__(self):
        self.interfaces = {}
        self.parser = argparse.ArgumentParser()
        self.sparsers = self.parser.add_subparsers()

        self.dir = None

        self.options(self.parser)

    def run(self):
        """
        Called after interfaces have registered to parse arguments and
        execute operations
        """
        args = self.parser.parse_args()
        logger.debug(args)
        self.call(args)

    def options(self, parser):
        """
        Adds arguments to the parser

        Parameters
        ----------
        parser : argparse.ArgumentParser
            parser to add args to
        """
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

        parser.add_argument(
            '--back', action='store_true')

        parser.add_argument(
            '--noback', action='store_true')

    def call(self, args):
        """
            Called when executing args

            Parameters
            ----------
            args : argparse.Namespace
        """

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

        if args.back:
            config.back_update = True
        elif args.noback:
            config.back_update = False

        if 'func' in args:
            args.func(args)

    def add(self, interface):
        """
        Register an interface with the UI

        Parameters
        ----------
        interface : ui.Interface
            Interface to be added
        """
        command = interface.command

        sparser = self.sparsers.add_parser(command)
        sparser.set_defaults(func=interface.call)

        interface.options(sparser)
        self.interfaces[command] = interface

    def f(self, fname):
        """
            Prepend directory to the file path if it was specified

            Parameters
            ----------
                fname : str
                    filename to modify
        """
        if fname == '-':
            return None
        if self.dir:
            return os.path.join(self.dir, fname)
        else:
            return fname

    def set_dir(self, dir_):
        if not os.path.isdir(dir_):
            raise ValueError(
                '%s Does not point to a valid directory' % dir_)

        if dir_[-1] == '/':
            dir_ = dir_[:-1]

        self.dir = dir_


class Interface:
    """
    Interface that defines a set of options and operations.
    Designed to be subclassed and overriden
    """

    def __init__(self, ui):
        """
        Initialize this interface and register it with the UI.

        Parameters
        ----------
        ui : ui.UI
            UI to register with
        """
        self.ui = ui
        ui.add(self)
        self.init()

    def init(self):
        """
        Method called on init, after having registered with ui
        """
        pass

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        pass

    def options(self, parser):
        """
        Add options to the parser
        """
        pass

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """
        pass

    ###############################################################

    def save(self, object, fname):
        """
        Pickle and save an object

        Parameters
        ----------
        object : object
            Object to be saved
        fname : str
            Filepath to save object to
        """
        if fname is not None:
            save_pickle(object, fname)

    def load(self, fname):
        """
        Load pickled object from file

        Parameters
        ----------
        fname : str
            Location of file
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
        logger.info(args)

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
                logger.info(fname)
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

        parser.add_argument(
            '--presrec', nargs=1,
            metavar='file')

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

        parser.add_argument(
            '--test-reorder', action='store_true')

        parser.add_argument(
            '--scores-from-csv', nargs=1)

        parser.add_argument(
            '--scores-to-csv', nargs=1)

        parser.add_argument(
            '--export-user-scores', nargs=1,
            help='Export user scores to csv')

    def call(self, args):
        swap = None
        score_export = None

        if args.load:
            obj = self.load(args.load[0])

            if isinstance(obj, SWAP):
                swap = obj
                score_export = swap.score_export()
            elif isinstance(obj, ScoreExport):
                score_export = obj

        if args.scores_from_csv:
            fname = args.scores_from_csv[0]
            score_export = ScoreExport.from_csv(fname)

        if args.run:
            swap = self.run_swap(args)
            score_export = swap.score_export()

        if swap is not None:

            if args.save:
                manifest = self.manifest(swap, args)
                self.save(swap, self.f(args.save[0]), manifest)

            if args.subject:
                fname = self.f(args.subject[0])
                plots.traces.plot_subjects(swap.history_export(), fname)

            if args.user:
                fname = self.f(args.user[0])
                plots.plot_user_cm(swap, fname)

            if args.utraces:
                fname = self.f(args.user[0])
                plots.traces.plot_user(swap, fname)

            if args.log:
                fname = self.f(args.log[0])
                write_log(swap, fname)

            if args.stats:
                s = swap.stats_str()
                print(s)
                logger.debug(s)

            if args.test:
                from swap.utils.golds import GoldGetter
                gg = GoldGetter()
                logger.debug('applying new gold labels')
                swap.set_gold_labels(gg.golds)
                swap.process_changes()
                logger.debug('done')

            if args.test_reorder:
                self.reorder_classifications(swap)

            if args.export_user_scores:
                fname = self.f(args.export_user_scores[0])
                self.export_user_scores(swap, fname)

        if score_export is not None:
            if args.save_scores:
                fname = self.f(args.save_scores[0])
                self.save(score_export, fname)

            if args.hist:
                fname = self.f(args.hist[0])
                plots.plot_class_histogram(fname, score_export)

            if args.dist:
                data = [s.getScore() for s in swap.subjects]
                plots.plot_pdf(data, self.f(args.dist[0]), swap,
                               cutoff=float(args.dist[1]))

            if args.presrec:
                fname = self.f(args.presrec[0])
                plots.distributions.sklearn_purity_completeness(
                    fname, score_export)

            if args.scores_to_csv:
                self.scores_to_csv(score_export, args.scores_to_csv[0])

        if args.diff:
            self.difference(args)

        if args.shell:
            import code
            from swap import ui
            assert ui

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

    def reorder_classifications(self, swap):
        import random
        import progressbar
        with progressbar.ProgressBar(
                max_value=len(swap.subjects)) as bar:
            n = 0
            for subject in swap.subjects:
                bar.update(n)

                ids = [t.id for t in subject.ledger]
                ids = list(sorted(ids, key=lambda item: random.random()))

                previous = None
                for i, id_ in enumerate(ids):
                    t = subject.ledger.get(id_)
                    t.order = i
                    t.right = None

                    if previous is None:
                        t.left = None
                    else:
                        previous.right = t
                        t.left = previous

                    subject.ledger.update(id_)
                    previous = t

                n += 1
        print(n)

        swap.process_changes()
        return swap

    def scores_to_csv(self, score_export, fname):
        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for score in score_export.scores.values():
                writer.writerow((score.id, score.gold, score.p))

    def export_user_scores(self, swap, fname):
        logger.debug('Exporting user scores to %s' % fname)
        with open(fname, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for user in swap.users:
                writer.writerow((user.id, *user.score, len(user.ledger)))
        logger.debug('done')

    # def scores_from_csv(self, fname):
    #     import csv
    #     from swap.utils.scores import Score, ScoreExport
    #     data = {}
    #     with open(fname) as csvfile:
    #         reader = csv.reader(csvfile)
    #         for i, g, p in reader:
    #             i = int(i)
    #             g = int(g)
    #             p = float(p)
    #             data[i] = Score(i, g, p)

    #     return ScoreExport(data, new_golds=False)

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

        p_args = []
        args_ = args.diff[1: -1]
        args_ = [tuple(args_[i: i + 2]) for i in range(0, len(args_), 2)]
        for label, fname in args_:
            _, extension = os.path.splitext(fname)
            if extension == '.csv':
                scores = ScoreExport.from_csv(fname)
            elif extension == '.pkl':
                scores = load_pickle(fname)

            p_args.append((label, scores))

        fname = self.f(args.diff[-1])

        print(p_args)

        # other = [load_pickle(x) for x in args.diff[1:]]
        plots.performance.p_diff(base, p_args, fname)


class ScoresInterface(Interface):
    """
        Customized interface for swap scores analysis
    """

    def __init__(self, ui):
        """
        Initialize this interface and register it with the UI.

        Parameters
        ----------
        ui : ui.UI
            UI to register with
        """
        self.ui = ui
        ui.add(self)
        self.init()

    # def init(self):
    #     """
    #     Method called on init, after having registered with ui
    #     """
    #     pass

    @property
    def command(self):
        """
        Command used to select parser.

        For example, this would return 'swap' for SWAPInterface
        and 'roc' for RocInterface
        """
        return 'scores'

    def options(self, parser):
        """
        Add options to the parser
        """
        parser.add_argument(
            '-a', '--add', nargs=2, action='append')

        parser.add_argument(
            '--diff', nargs=1)

        parser.add_argument(
            '--user', nargs=1)

        parser.add_argument(
            '--output', nargs=1)

        parser.add_argument(
            '--xaxis', nargs=1)

        parser.add_argument(
            '--yaxis', nargs=1)

        parser.add_argument(
            '--aspect-ratio', nargs=1)

        parser.add_argument(
            '--user-diff', nargs=2)

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """
        if args.output:
            output = self.f(args.output[0])
        else:
            output = None

        if args.diff:
            base = args.diff[0]
            self.difference(base, output, args)

        elif args.user:
            self.user(args.user[0], output, args)

        elif args.user_diff:
            self.user_diff(args.user_diff, output, args)

    def difference(self, base, output, args):
        base = self.load(base)
        print(11, base, output, args)

        p_args = []

        for label, fname in args.add:
            p_args.append((label, self.load(fname)))

        kwargs = {}
        if args.yaxis:
            kwargs['y_axis'] = args.yaxis[0]
        if args.xaxis:
            kwargs['x_axis'] = args.xaxis[0]
        if args.aspect_ratio:
            kwargs['aspect'] = eval(args.aspect_ratio[0])

        print(p_args)

        # other = [load_pickle(x) for x in args.diff[1:]]
        plots.performance.p_diff(base, p_args, output, **kwargs)

    def user(self, fname, output, args):
        data = self.load_user(fname)

        plots.performance.plot_confusion_matrix(
            data, "User Confusion Matrices", output)

    def user_diff(self, users, output, args):
        a = self.load_user(users[0], type_=dict)
        b = self.load_user(users[1], type_=dict)

        data = []
        for id_ in a:
            if id_ in b:
                x, y, n = zip(a[id_], b[id_])

                x = x[1] - x[0]
                y = y[1] - y[0]
                n = n[1] - n[0]

                data.append((x, y, n))

        plots.performance.plot_matrix_difference(
            data, "Confusion Matrix Difference", output)

    def load(self, fname):
        _, extension = os.path.splitext(fname)

        if extension == '.pkl':
            return super().load(fname)
        elif extension == '.csv':
            return ScoreExport.from_csv(fname)

    def load_user(self, fname, type_=list):
        logger.info('loading csv')
        if type_ is list:
            data = []
            with open(fname) as csvfile:
                reader = csv.reader(csvfile)
                for line in reader:
                    id_, s0, s1, n = line
                    data.append((float(s0), float(s1), int(n)))
        elif type_ is dict:
            data = {}
            with open(fname) as csvfile:
                reader = csv.reader(csvfile)
                for line in reader:
                    id_, s0, s1, n = line
                    data[id_] = (float(s0), float(s1), int(n))

        else:
            data = None

        logger.info('done')
        return data


class CaesarInterface(Interface):
    """
    Interface to launch the caesar app
    """

    def init(self):
        """
        Method called on init, after having registered with ui
        """
        pass

    @property
    def command(self):
        return 'caesar'

    def options(self, parser):
        parser.add_argument(
            '--load', nargs=1)

        parser.add_argument(
            '--run', action='store_true')

        parser.add_argument(
            '--port', nargs=1)

    def call(self, args):
        """
        Define what to do if this interface's command was passed
        """
        swap = None

        if args.port:
            config.caesar.swap.port = int(args.port[0])

        if args.load:
            swap = self.load(args.load[0])

        if args.run:
            self.run(swap)

    @staticmethod
    def run(swap=None):
        control = caesar.init_threader(swap)
        api = caesar.API(control)
        api.run()


def load_pickle(fname):
    """
        Loads a pickled object from file
    """
    try:
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        return data
    except Exception as e:
        logger.error('Error load file %s', fname)
        raise e


def save_pickle(object_, fname):
    """
        Pickles and saves an object to file
    """
    sys.setrecursionlimit(10000)
    with open(fname, 'wb') as file:
        pickle.dump(object_, file)


def run(*interfaces):
    """
        Run the interface

        Args:
            interface: Custom interface subclass to use
    """
    ui = UI()
    RocInterface(ui)
    SWAPInterface(ui)
    ScoresInterface(ui)
    CaesarInterface(ui)

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
        _, extension = os.path.splitext(fname)
        logger.info(label, fname, load)

        self.i += 1

        if extension == '.csv':
            return (label, ScoreExport.from_csv(fname).roc())
        else:
            obj = load(fname)

            return (label, self._get_export(obj))


def write_log(swap, fname):
    with open(fname, 'w') as file:
        file.writelines(swap.debug_str())


if __name__ == "__main__":
    # run()
    pass
