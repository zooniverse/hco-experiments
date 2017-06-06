#!/usr/bin/env python

from swap.control import Control
from swap.swap import SWAP
import swap.config.logger as logging

logging.init(__name__, __file__)

assert Control
assert SWAP
