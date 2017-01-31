#!/usr/bin/env python
################################################################
# Script to test Mongo functionality

import swap.mongo as mongo

a = mongo.DB()

def test_test():
    assert(a.test() == 1)