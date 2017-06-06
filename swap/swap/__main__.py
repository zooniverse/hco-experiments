#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm

import sys
import os
import logging

dir_ = os.path.dirname(os.path.abspath(__file__))
if os.path.samefile(dir_, sys.path[0]):
    sys.path = sys.path[1:]

import swap
from swap import ui

logger = logging.getLogger(swap.__name__)


def main():
    try:
        ui.run()
    except Exception as e:
        logger.critical(e)
        raise e


if __name__ == "__main__":
    main()
