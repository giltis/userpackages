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
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import logging
import sys
import yaml
import importlib
import os
logger = logging.getLogger(__name__)


# read yaml modules
with open((os.path.dirname(os.path.realpath(__file__)) + os.sep +
           'modules.yaml'), 'r') as modules:
    import_dict = yaml.load(modules)
    print('import_dict: {0}'.format(import_dict))


def get_modules():
    # import the hand-built VisTrails modules
    try:
        import_modules = import_dict['import_modules']
        print('import_modules: {0}'.format(import_modules))
        pymods = [importlib.import_module(module_name, module_path)
                  for module_path, mod_lst in six.iteritems(import_modules)
                  for module_name in mod_lst]
    except ImportError as ie:
        msg = ("importing {0} failed\n" "Original Error: "
               "{1}".format(module_name, module_path, ie))
        print(msg)
        logging.error(msg)
        six.reraise(*sys.exc_info())
    else:
        print('imported hand-built VT modules: {0}'.format(pymods))
        return [vtmod for mod in pymods for vtmod in
                mod.vistrails_modules()]

# # init the modules list
_modules = get_modules()