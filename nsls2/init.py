'''
Created on Apr 29, 2014

@author: edill
'''

# local packages to import
import vis, broker

# create a list of module lists that need to be registered in the nsls2 package
pymod_list = [vis, broker]

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