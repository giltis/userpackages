'''
Created on Apr 29, 2014

@author: edill
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six


# create a single list of modules that need to be registered in
# the nsls2 package
pymod_list = []

# local packages to import
try:
    from . import vis
except:
    print("importing vis failed")
else:
    pymod_list.append(vis)

try:
    import broker
except:
    print("importing broker failed")
else:
    pymod_list.append(broker)
    pass

try:
    from . import io
except:
    print("importing io failed")
else:
    pymod_list.append(io)


# register the things we imported successfully with vistrails
def get_modules():
    vistrails_modules = []
    for python_modules in pymod_list:
        for vismod in python_modules.vistrails_modules():
            vistrails_modules.append(vismod)
    return vistrails_modules

# init the modules list
_modules = get_modules()