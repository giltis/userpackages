'''
Created on Apr 29, 2014

@author: edill
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
# local packages to import
from . import vis, broker, io

# create a list of module lists that need to be registered in the nsls2 package
pymod_list = [vis, broker, io]

# create a single list of modules that need to be registered in
# the nsls2 package
def get_modules():
    vistrails_modules = []
    for python_modules in pymod_list:
        for vismod in python_modules.vistrails_modules():
            vistrails_modules.append(vismod)
    return vistrails_modules

# init the modules list
_modules = get_modules()