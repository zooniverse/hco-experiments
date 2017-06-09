#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm

import swap
from swap import ui
import swap.config.logger as log

logger = log.get_logger(swap.__name__)


def main():
    try:
        ui.run()
    except Exception as e:
        logger.critical(e)
        raise e


if __name__ == "__main__":
    main()
