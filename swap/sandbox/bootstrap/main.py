#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels

from swap.control import Control
from swap.swap import SWAP


def main():
    pass


class BootstrapControl(Control):
    
    def __init__(self, p0, epsilon, golds):
        pass

    def getClassifications(self):
        pass

    def process(self):
        pass


class BootstrapCursor:
    def __init__(self, golds):
        # Create the gold cursor
        # Create the cursor for all remaining classifications
        pass

    def __iter__(self):
        return self

    def next(self):
        # First iterate through gold cursor
        # Iterate through other cursor once gold is depleted
        # http://anandology.com/python-practice-book/iterators.html#the-iteration-protocol
        pass


if __name__ == "__main__":
    main()
