import yaml
import os

class Config:
    def __init__(self):
        path = os.path.dirname(os.path.realpath(__file__))
        f = open('%s/config.yaml' % path, 'r')
        self.config = yaml.load(f)