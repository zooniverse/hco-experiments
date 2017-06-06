#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels
import swaptools
import swaptools.ui

import logging

logger = logging.getLogger(swaptools.__name__)


def main():
    try:
        swaptools.ui.run()
    except Exception as e:
        if not isinstance(e, KeyboardInterrupt):
            logger.exception(e)
        else:
            logger.error('Keyboard interrupt\n')
        raise e


if __name__ == "__main__":
    main()
