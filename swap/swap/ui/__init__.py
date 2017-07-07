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
import swap.caesar.app as caesar

from swap.utils.scores import ScoreExport
from swap.swap import SWAP

from swap.ui.ui import UI
from swap.ui.scores import RocInterface, ScoresInterface
from swap.ui.swap import SWAPInterface
from swap.ui.caesar import CaesarInterface
from swap.ui.admin import AdminInterface

import pickle
import argparse
import os
import sys
import csv

import logging
logger = logging.getLogger(__name__)

__author__ = "Michael Laraia"


def _init_ui(interfaces=None):
    ui = UI()
    AdminInterface(ui)
    SWAPInterface(ui)
    CaesarInterface(ui)
    ScoresInterface(ui)
    RocInterface(ui)

    if interfaces is not None:
        for interface in interfaces:
            interface(ui)

    return ui


def _get_parser():
    return _init_ui().parser


def run(*interfaces):
    """
        Run the interface

        Args:
            interface: Custom interface subclass to use
    """

    ui = _init_ui(interfaces)
    ui.run()


if __name__ == "__main__":
    # run()
    pass
