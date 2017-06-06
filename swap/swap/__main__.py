#!/usr/bin/env python
################################################################
# Main entrypoint for the processing algorithm

import sys
import os

dir_ = os.path.dirname(os.path.abspath(__file__))
if os.path.samefile(dir_, sys.path[0]):
    sys.path = sys.path[1:]


from swap import ui
import swap.config.logger as logging


def main():
    logging.init(__name__, __file__)
    ui.run()


if __name__ == "__main__":
    main()
