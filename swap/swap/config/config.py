################################################################
# Configuration module to handle local config setup

import yaml
import os

class Config:
    def __init__(self):
        path = os.path.dirname(os.path.realpath(__file__))
        
        f = open('%s/config.yaml' % path, 'r')
        settings = yaml.load(f)
        f.close()

        self.__dict__.update(settings)