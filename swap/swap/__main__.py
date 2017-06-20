#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm

import swap
from swap import ui

import logging

logger = logging.getLogger(swap.__name__)


def main():
    try:
        ui.run()
    except Exception as e:
        logger.critical(e)
        raise e


if __name__ == "__main__":
    main()
