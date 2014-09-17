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
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
import numpy as np
import logging
from vistrails.core.modules.basic_modules import Constant
from vttools.wrap_lib import sig_map
logger = logging.getLogger(__name__)
#
# class ImageStack(Module):
#     # list of 2-d images
#     pass


class UBMatrix(Constant):
    """Module to specify a 3x3 matrix for VisTrails typing purposes

    Any module that uses this as an input port should look for the 'value'
    attribute to obtain the 3x3 matrix

    Attributes
    ----------
    default_value : ndarray
        3x3 array representing the ub matrix
    """

    _settings = ModuleSettings(abstract=True)
    _output_ports = [OPort(name='val_as_arr', signature='basic:Variant'),
                     OPort(name='value', signature='UBMatrix'),
                     OPort(name='value_as_str', signature='basic:String')]
    _input_ports = [IPort(name='value', signature='UBMatrix')]
    default_value = np.zeros((3, 3))

    def __init__(self, ub_mat_list):
        """
        Parameters
        ----------
        ub_mat_list : list
            List of 3 lists of length 3 that represents the ub matrix output
            from the data broker
        """
        super(UBMatrix, self).__init__()
        self.value = np.asarray(ub_mat_list)
        if self.value.shape != (3, 3):
            raise ValueError("ub_mat_list is not formatted correctly.  Expected"
                             "a 3x3 array, or something that will result in a"
                             "3x3 array when np.asarray(input) is called. "
                             "Input value: {0}\nResult of np.asarray(input): "
                             "{1}\nnp.asarray(input).shape: {2}"
                             "".format(ub_mat_list, self.value, self.value.shape))

    def translate_to_python(self, x):
        return np.asarray(x)

    def translate_to_string(self):
        return six.text_type(self.value)

    def validate(self, v):
        if v.shape == (3, 3):
            return True
        return False

    def __repr__(self):
        return six.text_type(self.value)

    def compute(self):
        if self.value is None:
            self.value = self.get_input('value')

        self.set_output('val_as_arr', self.value)
        self.set_output('value', self)
        self.set_output('value', self.__repr__)


# add the pararmeter name 'ub' to the signature map in the library_wrapper
# sig_map['ub'] = 'org.vistrails.vistrails.NSLS2:UBMatrix'


def vistrails_modules():
    # return [UBMatrix]
    return []