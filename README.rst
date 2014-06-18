Progressbar
===============================================================================

A class to display a progressbar while doing a long running task in Python.


Simple Example
----------------------------------------

import progressbar

import time

l = range(1,100)

for i in progressbar.loop(l):
    time.sleep(0.5)

