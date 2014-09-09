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
    """
    def grid3d(q, img_stack,
           nx=None, ny=None, nz=None,
           xmin=None, xmax=None, ymin=None,
           ymax=None, zmin=None, zmax=None):
    \"""Grid irregularly spaced data points onto a regular grid via histogramming


    This function will process the set of reciprocal space values (q), the
    image stack (img_stack) and grid the image data based on the bounds
    provided, using defaults if none are provided.

    Parameters
    ----------
    q : ndarray
        (Qx, Qy, Qz) - HKL values - Nx3 array
    img_stack : ndarray
        Intensity array of the images
        dimensions are: [num_img][num_rows][num_cols]
    nx : int, optional
        Number of voxels along x
    ny : int, optional
        Number of voxels along y
    nz : int, optional
        Number of voxels along z
    xmin : float, optional
        Minimum value along x. Defaults to smallest x value in q
    ymin : float, optional
        Minimum value along y. Defaults to smallest y value in q
    zmin : float, optional
        Minimum value along z. Defaults to smallest z value in q
    xmax : float, optional
        Maximum value along x. Defaults to largest x value in q
    ymax : float, optional
        Maximum value along y. Defaults to largest y value in q
    zmax : float, optional
        Maximum value along z. Defaults to largest z value in q

    Returns
    -------
    mean : ndarray
        intensity grid.  The values in this grid are the
        mean of the values that fill with in the grid.
    occupancy : ndarray
        The number of data points that fell in the grid.
    std_err : ndarray
        This is the standard error of the value in the
        grid box.
    oob : int
        Out Of Bounds. Number of data points that are outside of
        the gridded region.
    bounds : list
        tuple of (min, max, step) for x, y, z in order: [x_bounds,
        y_bounds, z_bounds]

    \"""

    q = np.atleast_2d(q)
    q.shape
    if q.ndim != 2:
        raise ValueError("q.ndim must be a 2-D array of shape Nx3 array. "
                         "You provided an array with {0} dimensions."
                         "".format(q.ndim))
    if q.shape[1] != 3:
        raise ValueError("The shape of q must be an Nx3 array, not {0}X{1}"
                         " which you provided.".format(*q.shape))

    # set defaults for qmin, qmax, dq
    qmin = np.min(q, axis=0)
    qmax = np.max(q, axis=0)
    dqn = [_defaults['nx'], _defaults['ny'], _defaults['nz']]

    # pad the upper edge by just enough to ensure that all of the
    # points are in-bounds with the binning rules: lo <= val < hi
    qmax += np.spacing(qmax)

    # check for non-default input
    for target, input_vals in ((dqn, (nx, ny, nz)),
                               (qmin, (xmin, ymin, zmin)),
                               (qmax, (xmax, ymax, zmax))):
        for j, in_val in enumerate(input_vals):
            if in_val is not None:
                target[j] = in_val

    # format bounds
    bounds = np.array([qmin, qmax, dqn]).T

    # creating (Qx, Qy, Qz, I) Nx4 array - HKL values and Intensity
    # getting the intensity value for each pixel
    q = np.insert(q, 3, np.ravel(img_stack), axis=1)

    #            3D grid of the data set
    # starting time for gridding
    t1 = time.time()

    # call the c library
    mean, occupancy, std_err, oob = ctrans.grid3d(q, qmin, qmax, dqn, norm=1)

    # ending time for the gridding
    t2 = time.time()
    logger.info("Done processed in {0} seconds".format(t2-t1))

    # No. of values zero in the grid
    empt_nb = (occupancy == 0).sum()

    # log some information about the grid at the debug level
    if oob:
        logger.debug("There are %.2e points outside the grid {0}".format(oob))
    logger.debug("There are %2e bins in the grid {0}".format(mean.size))
    if empt_nb:
        logger.debug("There are %.2e values zero in the grid {0}"
                     "".format(empt_nb))

    return mean, occupancy, std_err, oob, bounds
    """
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

    _optional = ['nx', 'ny', 'nz', 'xmin', 'ymin', 'zmin', 'xmax',
                 'ymax', 'zmax']
    _mandatory = ['q', 'img_stack']
    _input_dict = {}

    def compute(self):
        mandatory = self._mandatory
        optional = self._optional
        input_dict = self._input_dict
        # gather mandatory input
        img_stack = self.get_input('img_stack')
        q = self.get_input('q')
        # input_dict = {m: self.get_input(m) for m in mandatory}
        # print('len(q), q.__class__: {0}, {1}'.
        #       format(len(q), q.__class__))
        # print('len(q[0], q[0].__class__: {0}, {1}'.
        #       format(len(q[0]), q[0].__class__))
        # print('len(q[0][0], q[0][0].__class__: {0}, {1}'.
        #       format(len(q[0][0]), q[0][0].__class__))
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
        self.set_output('bounds', bounds)
