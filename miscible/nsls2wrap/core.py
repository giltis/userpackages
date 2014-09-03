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

from nsls2.core import grid3d


class Grid(Module):
    _settings = ModuleSettings(namespace="nsls2|core")

    _input_ports = [
        IPort(name='q', label='hkl values in N x 3 array',
              signature='basic:List'),
        IPort(name='img_stack', label='N x 1 array of pixel intensities',
              signature='basic:List'),
        IPort(name='nx',
              label='x voxel step size',
              signature='basic:Integer', optional=True),
        IPort(name='ny',
              label='y voxel step size',
              signature='basic:Integer', optional=True),
        IPort(name='nz',
              label='z voxel step size',
              signature='basic:Integer', optional=True),
        IPort(name='xmin',
              label='minimum value in x',
              signature='basic:Float', optional=True),
        IPort(name='ymin',
              label='minimum value in y',
              signature='basic:Float', optional=True),
        IPort(name='zmin',
              label='minimum value in z',
              signature='basic:Float', optional=True),
        IPort(name='xmax',
              label='maximum value in x',
              signature='basic:Float', optional=True),
        IPort(name='ymax',
              label='maximum value in y',
              signature='basic:Float', optional=True),
        IPort(name='zmax',
              label='maximum value in z',
              signature='basic:Float', optional=True)
    ]

    _output_ports = [
        OPort(name='mean', signature='basic:List'),
        OPort(name='std_err', signature='basic:List'),
        OPort(name='occupancy', signature='basic:List'),
        OPort(name='oob', signature="basic:Integer")
    ]

    def compute(self):
        mandatory = ['q', 'img_stack']
        optional = ['nx', 'ny', 'nz', 'xmin', 'ymin', 'zmin', 'xmax',
                    'ymax', 'zmax']
        input_dict = {}
        # gather mandatory input
        img_stack = self.get_input('img_stack')
        q = self.get_input('q')
        # input_dict = {m: self.get_input(m) for m in mandatory}
        print('len(q), q.__class__: {0}, {1}'.
              format(len(q), q.__class__))
        print('len(q[0], q[0].__class__: {0}, {1}'.
              format(len(q[0]), q[0].__class__))
        print('len(q[0][0], q[0][0].__class__: {0}, {1}'.
              format(len(q[0][0]), q[0][0].__class__))
        # q = np.asarray(q)
        # print('q.shape, q.__class__: {0}, {1}'.
        #       format(q.shape, q.__class__))
        # print('Grid line 220')
        lst = q
        stride = len(lst[0])
        out_arr = np.zeros((stride * len(lst), 3))
        for idx, (arr) in enumerate(lst):
            start = idx * stride
            stop = (idx + 1) * stride
            out_arr[start:stop] = arr
        q = out_arr
        print('q.shape, q.__class__: {0}, {1}'.
              format(q.shape, q.__class__))
        if isinstance(img_stack, list):
            img_stack = np.asarray(img_stack)

        for o in optional:
            try:
                input_dict[o] = self.get_input(o)
            except ModuleError:
                # will be thrown if there is no input on this port
                logger.debug("No input on port: {0}".format(o))
        mean, std_err, occu, oob, bounds = grid3d(q, img_stack, **input_dict)

        self.set_output('mean', mean)
        self.set_output('std_err', std_err)
        self.set_output('occupancy', occu)
        self.set_output('oob', oob)
        self.set_output('bounds', 'bounds')
