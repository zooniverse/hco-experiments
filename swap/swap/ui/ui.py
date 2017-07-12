
import swap.config as config
import swap.db
from swap.ui.utils import save_pickle, load_pickle

import argparse
import os

import logging
logger = logging.getLogger(__name__)


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
            help='Save any files created by swap to a different directory')

        parser.add_argument(
            '--p0', nargs=1,
            help='Define prior probability')

        parser.add_argument(
            '--pow', action='store_true',
            help='controversial and consensus aggregation method')

        parser.add_argument(
            '--multiply', action='store_true',
            help='controversial and consensus aggregation method')

        parser.add_argument(
            '--back', action='store_true',
            help='Run swap in back_update mode (static swap)')

        parser.add_argument(
            '--noback', action='store_true',
            help='Run swap without back_update mode (dynamic swap)')

        parser.add_argument(
            '--config-file', nargs=1,
            metavar='path_to_config_override',
            help='Override config options with custom python module')

        parser.add_argument(
            '--db', nargs=1,
            help='Override database name in config'
        )

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

        # if args.epsilon:
        #     config.epsilon = float(args.epsilon[0])

        if args.pow:
            config.controversial_version = 'pow'
        elif args.multiply:
            config.controversial_version = 'multiply'

        if args.back:
            config.back_update = True
        elif args.noback:
            config.back_update = False

        if args.config_file:
            config.import_config(args.config_file[0])

        if args.db:
            config.database.name = args.db[0]

        swap.db.DB._reset()

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

    @staticmethod
    def save(obj, fname):
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
            save_pickle(obj, fname)

    @staticmethod
    def load(fname):
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
