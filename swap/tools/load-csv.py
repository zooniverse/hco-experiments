#!/usr/bin/env python
################################################################
# Script to load a csv file to the mongo database, 
# as described in the config.yaml

from swap.config import Config
from swap import Mongo


def main():
    c = Config()
    config = c.config


    

if __name__ == "__main__":
    main()