# ######################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Redistribution and use in source and binary forms, with or without   #
# modification, are permitted provided that the following conditions   #
# are met:                                                             #
#                                                                      #
# * Redistributions of source code must retain the above copyright     #
#   notice, this list of conditions and the following disclaimer.      #
#                                                                      #
# * Redistributions in binary form must reproduce the above copyright  #
#   notice this list of conditions and the following disclaimer in     #
#   the documentation and/or other materials provided with the         #
#   distribution.                                                      #
#                                                                      #
# * Neither the name of the Brookhaven Science Associates, Brookhaven  #
#   National Laboratory nor the names of its contributors may be used  #
#   to endorse or promote products derived from this software without  #
#   specific prior written permission.                                 #
#                                                                      #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       #
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                          #
########################################################################
'''
Created on Apr 29, 2014
'''
from __future__ import (absolute_import,
                        division,
                        print_function,
                        unicode_literals
)
import logging
logger = logging.getLogger(__name__)


# create a single list of modules that need to be registered in
# the nsls2 package
pymod_list = []

# local packages to import
from vttools import wrap_lib

import_list_funcs = [
    {'func_name': 'grid3d',
     'module_path': 'nsls2.core',
     'add_input_dict': True,
     'namespace': 'core'},
    {'func_name': 'process_to_q',
     'module_path': 'nsls2.recip',
     'add_input_dict': True,
     'namespace': 'recip'},
    {'func_name': 'bin_1D',
     'module_path': 'nsls2.core',
     'namespace': 'core'},
    # {'func_name': 'emission_line_search',
    #  'module_path': 'nsls2.constants',
    #  'has_dict_input': True,
    #  'namespace': 'core'},
    # {'func_name': 'snip_method',
    #  'module_path': 'nsls2.fitting.model.background',
    #  'has_dict_input': True,
    #  'namespace': 'core'},
    # {'func_name': 'gauss_peak',
    #  'module_path': 'nsls2.fitting.model.physics_peak',
    #  'has_dict_input': True,
    #  'namespace': 'core'},
    # {'func_name': 'gauss_step',
    #  'module_path': 'nsls2.fitting.model.physics_peak'},
    # {'func_name': 'gauss_tail',
    #  'module_path': 'nsls2.fitting.model.physics_peak'},
    # {'func_name': 'elastic_peak',
    #  'module_path': 'nsls2.fitting.model.physics_peak'},
    # {'func_name': 'compton_peak',
    #  'module_path': 'nsls2.fitting.model.physics_peak'},
    {'func_name': 'read_binary',
     'module_path': 'nsls2.io.binary'},
    # {'func_name': 'fit_quad_to_peak',
    #  'module_path': 'nsls2.spectroscopy'},
    # {'func_name': 'align_and_scale',
    #  'module_path': 'nsls2.spectroscopy'},
    # {'func_name': 'find_largest_peak',
    #  'module_path': 'nsls2.spectroscopy'},
    # {'func_name': 'integrate_ROI_spectrum',
    #  'module_path': 'nsls2.spectroscopy'},
    # {'func_name': 'integrate_ROI',
    #  'module_path': 'nsls2.spectroscopy'},
]


# register the things we imported successfully with vistrails
def vistrails_modules():
    wrap_lib.logger.setLevel(logging.INFO)
    # print(import_list_funcs[3])
    func_list = import_list_funcs
    return [wrap_lib.wrap_function(**func_dict) for func_dict in func_list]
    # func_dict = {'func_name': 'func_wrap_smoke_test',
    #              'module_path': '..autowrap_nsls2',
    #              'add_input_dict': False, 'namespace': 'wrapping test'},
    # # return wrap_lib.do_wrap(**func_dict)
    # return wrap_lib.run()

# init the modules list
# _modules = get_modules()
