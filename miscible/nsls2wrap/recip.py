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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import (Module, ModuleSettings,
                                                     ModuleError)
from vistrails.core.modules.config import IPort, OPort
import numpy as np
import logging
logger = logging.getLogger(__name__)

from nsls2.recip import process_grid, process_to_q


class QConversion(Module):
    _settings = ModuleSettings(namespace="nsls2|recip")

    _input_ports = [
        IPort(name='setting_angles',
              label='six angles of all the images - Nx6 array: delta, theta, '
                    'chi, phi, mu, gamma (degrees)',
              signature='basic:List'),
        IPort(name='detector_size',
              label='2 elements defining no. of pixels(size) in the'
                    ' detector X and Y direction(mm)',
              signature='basic:List'),
        IPort(name='pixel_size',
              label='2 elements defining the (x y) dimensions of the'
                    'pixel (mm)',
              signature='basic:List'),
        IPort(name='calibrated_center',
              label='2 elements defining the (x y) center of '
                    'the detector (mm)',
              signature='basic:List'),
        IPort(name='dist_sample',
              label='distance from the sample to the detector (mm)',
              signature='basic:Float'),
        IPort(name='wavelength',
              label='wavelength of incident radiation (Angstroms)',
              signature='basic:Float'),
        IPort(name='ub_mat',
              label='UB matrix (orientation matrix) 3x3 matrix',
              signature='basic:List'),
        IPort(name='calib_dict',
              label='Calibration dictionary from data broker',
              signature='basic:Dictionary')
    ]

    _output_ports = [
        OPort(name='tot_set', signature='basic:List'),
    ]

    def compute(self):
        mandatory = ['setting_angles', 'detector_size', 'pixel_size',
                     'calibrated_center', 'dist_sample', 'wavelength',
                     'ub_mat']
        dict_in = ['calib_dict']
        optional = []

        # gather mandatory input
        input_dict = {m: self.get_input(m) for m in mandatory}
        # unpack dictionary input first so that duplicate ports will override
        # the dictionary input
        for id in dict_in:
            try:
                adict = self.get_input(id)
                for k, v in six.iteritems(adict):
                    input_dict[k] = v
            except ModuleError:
                # will be thrown if there is no input on this port
                logger.debug("No input on port: {0}".format(id))

        # gather optional input
        for o in optional:
            try:
                input_dict[o] = self.get_input(o)
            except ModuleError:
                # will be thrown if there is no input on this port
                logger.debug("No input on port: {0}".format(o))

        tot_set = process_grid(**input_dict)

        self.set_output('tot_set', tot_set)


class Grid(Module):
    _settings = ModuleSettings(namespace="nsls2|recip")

    _input_ports = [
        IPort(name='tot_set', label='hkl values in N x 3 array',
              signature='basic:List'),
        IPort(name='istack', label='N x 1 array of pixel intensities',
              signature='basic:List'),
        IPort(name='q_min',
              label='Minimum voxel value: tuple or list of (x, y, z)',
              signature='basic:List', optional=True),
        IPort(name='q_max',
              label='Maximum voxel value: tuple or list of (x, y, z)',
              signature='basic:List', optional=True),
        IPort(name='dqn',
              label='Voxel step size: tuple or list of (x, y, z)',
              signature='basic:List', optional=True)
    ]

    _output_ports = [
        OPort(name='mean', signature='basic:List'),
        OPort(name='std_err', signature='basic:List'),
        OPort(name='occupancy', signature='basic:List'),
        OPort(name='num_outside_bounds', signature="basic:List")
    ]

    def compute(self):
        mandatory = ['tot_set', 'istack']
        optional = ['q_min', 'q_max', 'dqn']
        input_dict = {}
        # gather mandatory input
        input_dict = {m: self.get_input(m) for m in mandatory}

        for o in optional:
            try:
                input_dict[o] = self.get_input(o)
            except ModuleError:
                # will be thrown if there is no input on this port
                logger.debug("No input on port: {0}".format(o))

        mean, std_err, occu, oob = process_grid(**input_dict)

        self.set_output('mean', mean)
        self.set_output('std_err', std_err)
        self.set_output('occupancy', occu)
        self.set_output('num_outside_bounds', oob)
