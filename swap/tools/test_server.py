#!/usr/bin/env python
################################################################
# Script to test server functionality

import swap

server = swap.Server(.5,.5)

print(server.getClassifications())
