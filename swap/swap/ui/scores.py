################################################################
"""
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

import swap.plots as plots

from swap.utils.scores import ScoreExport
from swap.swap import SWAP
from swap.ui.ui import Interface

import os
import csv
import logging

logger = logging.getLogger(__name__)


class ScoresInterface(Interface):
    """
        Customized interface for swap scores analysis
    """

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

    @staticmethod
    def _get_export(obj):
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

        obj = load(fname)
        return (label, self._get_export(obj))
