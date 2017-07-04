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

from swap.control import Control
import swap.config as config
import swap.plots as plots
import swap.app.caesar_app as caesar

from swap.utils.scores import ScoreExport
from swap.swap import SWAP

from swap.ui.scores import RocInterface, ScoresInterface
from swap.ui.swap import SWAPInterface
from swap.ui.caesar import CaesarInterface

import pickle
import argparse
import os
import sys
import csv

import logging
logger = logging.getLogger(__name__)

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


def write_log(swap, fname):
    with open(fname, 'w') as file:
        file.writelines(swap.debug_str())


if __name__ == "__main__":
    # run()
    pass
