'''
Created on Apr 29, 2014

@author: edill
'''

import vis


mod_list = [vis.modules()]


def get_modules():
    modules = []
    for packages in mod_list:
        for mods in packages:
            modules.append(mods)
    return modules

_modules = get_modules()