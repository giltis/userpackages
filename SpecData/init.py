################################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven National       #
# Laboratory. All rights reserved.                                             #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided that the following conditions are met:  #
#                                                                              #
# * Redistributions of source code must retain the above copyright notice,     #
#   this list of conditions and the following disclaimer.                      #
#                                                                              #
# * Redistributions in binary form must reproduce the above copyright notice,  #
#  this list of conditions and the following disclaimer in the documentation   #
#  and/or other materials provided with the distribution.                      #
#                                                                              #
# * Neither the name of the European Synchrotron Radiation Facility nor the    #
#   names of its contributors may be used to endorse or promote products       #
#   derived from this software without specific prior written permission.      #
#                                                                              #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"  #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE    #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE   #
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE    #
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR          #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF         #
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS     #
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN      #
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)      #
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                                  #
################################################################################
from vistrails.core.modules.vistrails_module import Module, ModuleError
from vistrails.core.modules.config import IPort, OPort
from pyspec.ccd.transformations import FileProcessor, ImageProcessor
from pyspec.spec import SpecDataFile
import numpy as np


class SpecFile(Module):
    _input_ports = [
        IPort(name="spec_file_params", label="Spec File Parameters", \
              signature="gov.nsls2.spec.SpecData:SpecFileParams"),
        ]

    _output_ports = [
        OPort(name="spec_img_stack", signature="basic:List"),
        OPort(name="spec_metadata", signature="basic:Dictionary"),
        OPort(name="spec_file", signature="gov.nsls2.spec.SpecData:SpecFile")
        ]


    def __init__(self):
        Module.__init__(self)


    def compute(self):
        spec_params = self.get_input("spec_file_params")
        spec_file_root = spec_params.spec_file_root
        data_folder_path = spec_params.data_folder_path
        scan_no = spec_params.scan_number

        print spec_file_root
        print data_folder_path
        sf = SpecDataFile(spec_file_root, ccdpath=data_folder_path)
        scan = sf[scan_no]

        fp = FileProcessor(spec=scan)

        fp.process()
        arr_2d_stack = fp.getImage()

        self.set_output("spec_img_stack", arr_2d_stack)
        self.set_output("spec_file", self)
        self.fp = fp
        self.sf = sf
        self.scan = scan

class SpecFileParams(Module):
    _input_ports = [
        IPort(name="spec_file_root", label="Spec File Root", signature="basic:String"),
        IPort(name="data_folder_path", label="Data Folder Path", signature="basic:String"),
        IPort(name="scan_number", label="Scan number", signature="basic:Integer"),
        ]
    _output_ports = [
        OPort(name="spec_file_params", signature="gov.nsls2.spec.SpecData:SpecFileParams"),
        ]
    def compute(self):
        self.spec_file_root = self.get_input("spec_file_root")
        self.data_folder_path = self.get_input("data_folder_path")
        self.scan_number = self.get_input("scan_number")
        self.set_output("spec_file_params", self)

class Gridder(Module):
    _input_ports = [
        IPort(name="gridder_params", label="Parameters for Gridding", \
              signature="gov.nsls2.spec.SpecData:GridderParams"),
        ]
    _output_ports = [
        OPort(name="x_mesh", signature="basic:List"),
        OPort(name="y_mesh", signature="basic:List"),
        OPort(name="z_mesh", signature="basic:List"),
        OPort(name="masked_data", signature="basic:List"),
        OPort(name="raw_data", signature="basic:List"),
        OPort(name="occupancy", signature="basic:List"),
        OPort(name="std_dev", signature="basic:List"),
        OPort(name="gridder", signature="gov.nsls2.spec.SpecData:Gridder"),
        ]
    def compute(self):
        self.gridder_params = self.get_input("gridder_params")
        spec_file = self.gridder_params.spec_file
        ip = ImageProcessor(spec_file.fp)
        self.planes = ['HK', '']
        hkl_dims = self.gridder_params.hkl_dims

        ccd_crop = [5, 5, 0, 0]
        ccd_size = spec_file.fp.images[0].shape
        det_size_x = ccd_size[0]
        det_size_y = ccd_size[1]
        det_pix_size_x = 0.0135 * 2048 / det_size_x
        det_pix_size_y = 0.0135 * 2048 / det_size_y
        det_x0 = det_size_x / 2.0
        det_y0 = det_size_y / 2.0

        ip.setSpecScan(spec_file.scan)
        ip.setDetectorPos(355.0, 0)

        # sample orientation matrix is stored in spec file so this flag is enough
        ip.setFrameMode('hkl')

        ip.setDetectorProp(det_pix_size_x, det_pix_size_y, det_size_x, det_size_y, det_x0, det_y0)
        if ccd_crop != [0, 0, 0, 0]:
            ip.setDetectorMask(self.makeMask(spec_file.fp, ccd_crop, ccd_size))

        ip.setGridSize([hkl_dims[0], hkl_dims[2], hkl_dims[4]], \
                       [hkl_dims[1], hkl_dims[3], hkl_dims[5]],
                       self.gridder_params.bins_arr)
        ip.process()

        # masks any voxels with less than this number of hits
        ip.setGridMaskOnOccu(10)

        self.ip = ip

        X, Y, Z, I, E, N = ip.getGrid()
        raw = ip.gridData

        self.set_output("x_mesh", X)
        self.set_output("y_mesh", Y)
        self.set_output("z_mesh", Z)
        self.set_output("masked_data", I)
        self.set_output("raw_data", raw)
        self.set_output("occupancy", N)
        self.set_output("std_dev", E)
        self.set_output("gridder", self)



    def makeMask(self, fp, ccdcrop, ccdsize):
        """
            image. Sets pixel range specified from the boundries to 0
        """
        mask = np.ones(fp.images.shape, dtype=np.bool)
        mask[:, ccdcrop[0]:ccdsize[0] - ccdcrop[2], ccdcrop[1]:ccdsize[1] - ccdcrop[3]] = 0
        unMaskedSize = mask[:, ccdcrop[0]:ccdsize[0] - ccdcrop[2], ccdcrop[1]:ccdsize[1] - ccdcrop[3]].shape
        return mask

class GridderParams(Module):
    """ 
        GridderParams is just a package for the parameters required for gridding a
        non-regular set of points
    """
    _input_ports = [
        IPort(name="spec_file", label="Spec File", signature="gov.nsls2.spec.SpecData:SpecFile"),
        IPort(name="h_min", label="Minimum value for H", signature="basic:Float", optional=True),
        IPort(name="h_max", label="Maximum value for H", signature="basic:Float", optional=True),
        IPort(name="k_min", label="Minimum value for K", signature="basic:Float", optional=True),
        IPort(name="k_max", label="Maximum value for K", signature="basic:Float", optional=True),
        IPort(name="l_min", label="Minimum value for L", signature="basic:Float", optional=True),
        IPort(name="l_max", label="Maximum value for L", signature="basic:Float", optional=True),
        IPort(name="bins_x", label="Number of bins in x", signature="basic:Integer"),
        IPort(name="bins_y", label="Number of bins in y", signature="basic:Integer"),
        IPort(name="bins_z", label="Number of bins in z", signature="basic:Integer"),
        ]
    _output_ports = [
        OPort(name="gridder_params", signature="gov.nsls2.spec.SpecData:GridderParams"),
        ]

    def getScanProps(self, scan):
        h_range = [0.01, 0.01]; k_range = [0.012, 0.011];l_range = [0.018, 0.018]
        #=======================================================================
        # temp = scan.Tsam
        # energy = scan.Energy
        #=======================================================================
        # scan[0][0].H is the center of the detector
        # min(scan[0][0].H) is the minimum of all detectors
        # the -h_range[0] is the difference between the center of the
        # detector and the edge of the detector.
        #--------------------------------------------------------- h = scan.H[0]
        #--------------------------------------------------------- k = scan.K[0]
        #--------------------------------------------------------- l = scan.L[0]
        hkl_dims = [ min(scan.H) - h_range[0], max(scan.H) + h_range[1], \
              min(scan.K) - k_range[0], max(scan.K) + k_range[1], \
              min(scan.L) - l_range[0], max(scan.L) + l_range[1]]

        #=======================================================================
        # return hkl_dims, temp, energy
        #=======================================================================
        return hkl_dims

    def compute(self):
        self.spec_file = self.get_input("spec_file")
        if self.spec_file is not None:
            self.hkl_dims = self.getScanProps(self.spec_file.scan)

        # Check optional ports for values
        if self.has_input("h_min"):
            self.h_min = self.get_input("h_min")
        if self.has_input("h_max"):
            self.h_max = self.get_input("h_max")
        if self.has_input("k_min"):
            self.k_min = self.get_input("k_min")
        if self.has_input("k_max"):
            self.k_max = self.get_input("k_max")
        if self.has_input("l_min"):
            self.l_min = self.get_input("l_min")
        if self.has_input("l_max"):
            self.l_max = self.get_input("l_max")

        self.bins_x = self.get_input("bins_x")
        self.bins_y = self.get_input("bins_y")
        self.bins_z = self.get_input("bins_z")

        if self.hkl_dims is None:
            self.hkl_dims = [self.h_min, self.h_max,
                         self.k_min, self.k_max,
                         self.l_min, self.l_max]

        self.bins_arr = [self.bins_x, self.bins_y, self.bins_z]
        self.set_output("gridder_params", self)

class PlotGridded(Module):
    _input_ports = [
        IPort(name="gridder", label="Gridder instance",
              signature="gov.nsls2.spec.SpecData:Gridder"),
        ]

    _output_ports = [
        OPort(name="x", signature="basic:List"),
        OPort(name="y", signature="basic:List"),
        OPort(name="z", signature="basic:List"),
        OPort(name="title", signature="basic:String"),
        OPort(name="x_label", signature="basic:String"),
        OPort(name="y_label", signature="basic:String"),
        ]

    def compute(self):
        gridder = self.get_input("gridder")
        ip = gridder.ip
        hkl_range = gridder.gridder_params.hkl_dims
        planes = gridder.planes
        x, y, z, dz, lx, lz, dlz, limits, labels, titles = \
            self.get_xyz(ip.getGrid(), planes[0], hkl_range)

        self.set_output("x", x)
        self.set_output("y", y)
        self.set_output("z", z)
        self.set_output("x_label", labels[0])
        self.set_output("y_label", labels[1])
        self.set_output("title", titles[0])

    # this is probably subtracting a planar background
    # email vivek and ask him what the heck is going on
    def get_xyz(self, fullGrid, plane, hkl_dims):
        HKL = axis3 = 'HKL'
        for i in plane: axis3 = axis3.replace(i, '')

        hkl_range = [ [hkl_dims[0], hkl_dims[1]],
                      [hkl_dims[2], hkl_dims[3]],
                      [hkl_dims[4], hkl_dims[5]] ]
        H = fullGrid[0][:, 0, 0]
        K = fullGrid[1][0, :, 0]
        L = fullGrid[2][0, 0, :]

        H_Inds = [np.where(H >= hkl_range[0][0])[0][0], np.where(H <= hkl_range[0][1])[0][-1] + 1]
        K_Inds = [np.where(K >= hkl_range[1][0])[0][0], np.where(K <= hkl_range[1][1])[0][-1] + 1]
        L_Inds = [np.where(L >= hkl_range[2][0])[0][0], np.where(L <= hkl_range[2][1])[0][-1] + 1]

        grid = [grid_i[H_Inds[0]:H_Inds[1], K_Inds[0]:K_Inds[1], L_Inds[0]:L_Inds[1]] for grid_i in fullGrid]

        HHH = grid[0][:, :, :]
        KKK = grid[1][:, :, :]
        LLL = grid[2][:, :, :]

        ind1 = 1 + (HKL.find(axis3) <> 0) * len(HHH[:, 0, 0])
        ind2 = 1 + (HKL.find(axis3) <> 1) * len(HHH[0, :, 0])
        ind3 = 1 + (HKL.find(axis3) <> 2) * len(HHH[0, 0, :])

        HH = HHH[:ind1, :ind2, :ind3].squeeze()
        KK = KKK[:ind1, :ind2, :ind3].squeeze()
        LL = LLL[:ind1, :ind2, :ind3].squeeze()

        H = grid[0][:, 0, 0]
        K = grid[1][0, :, 0]
        L = grid[2][0, 0, :]

        z = grid[3][:, :, :].mean(HKL.find(axis3)) * 1e3
        dz = grid[4][:, :, :].mean(HKL.find(axis3)) * 1e3

        lz = z.mean(int('HKL'.find(plane[0]) < 'HKL'.find(plane[1]))) * 1e3
        dlz = np.sqrt((z ** 2).mean(int('HKL'.find(plane[0]) < 'HKL'.find(plane[1])))) * 1e3

        x_range = hkl_range[HKL.find(plane[0])]
        y_range = hkl_range[HKL.find(plane[1])]

        x_label = plane[0] + ' [r.l.u.]'
        y_label = plane[1] + ' [r.l.u.]'

        axis3_range = hkl_range[HKL.find(axis3)]
        slice_title = ' %s=[%.3f,%.3f]' % (axis3, axis3_range[0], axis3_range[1])
        cut_title = slice_title + (' %s=[%.3f,%.3f]' % (plane[1], y_range[0], y_range[1]))

        x = eval(plane[0] + plane[0])
        y = eval(plane[1] + plane[1])
        lx = eval(plane[0])

        return x, y, z, dz, \
               lx, lz, dlz, \
               [x_range, y_range], \
               [x_label, y_label], \
               [slice_title, cut_title]

class SpecFileProcessor(Module):
    _input_ports = [
        IPort(name="img_stack", label="Stack of 2D Images", \
              signature="basic:List"),
        IPort(name="has_dark", label="Are dark files present?", \
              signature="basic:Boolean", default=True, optional=True),
        IPort(name="spec_file", label="Spec File Object", \
              signature="gov.nsls2.spec.SpecData:SpecFile"),
        IPort(name="scan_numbers", label="List of scan numbers",
              signature="basic:List"),
        ]

    _output_ports = [
        OPort(name="single_img_array", signature="basic:List"),
        ]

    def compute(self):
        pass

class SpecScan(Module):
    _input_ports = [
        IPort(name="img_stack", label="Stack of 2D Images", \
              signature="basic:List")
        ]

    _output_ports = [
        OPort(name="single_img_array", signature="basic:List"),
        ]

    def compute(self):
        pass

class SpecMetadata(Module):
    _input_ports = [
        IPort(name="meta_data", label="Metadata from Spec Scan", \
              signature="basic:Dictionary"),
        ]

    def compute(self):
        pass

class ImageStackImageSelector(Module):
    _input_ports = [
        IPort(name="img_stack", label="Stack of 2D Images", \
              signature="basic:List"),
        IPort(name="img_no", label="Desired Image Number", \
              signature="basic:Integer"),
        ]

    _output_ports = [
        OPort(name="2D_img", signature="basic:List"),
        ]

    def compute(self):
        img_stack = self.get_input("img_stack")
        print "Image Stack class: {0}".format(img_stack.__class__)
        img_no = self.get_input("img_no")
        single_img = img_stack[img_no]
        self.set_output("2D_img", single_img)

class ImageStackSum(Module):
    _input_ports = [
        IPort(name="img_stack", label="Stack of 2D Images", \
              signature="basic:List"),
        ]

    _output_ports = [
        OPort(name="2D_img", signature="basic:List"),
        ]

    def compute(self):
        img_stack = self.get_input("img_stack")
        #=======================================================================
        # img_stack_np = (numpy.ndarray) img_stack
        #=======================================================================

        img_sum = img_stack[0]
        total_images = 0
        for i in range(1, len(img_stack)):
            img_sum.__add__(img_stack[i])
            total_images += 1

        img_sum.__mul__(1 / total_images)

        self.set_output("2D_img", img_sum)
class SwapAxes(Module):
    _input_ports = [
        IPort(name="axis1", label="Axis to swap", signature="basic:Integer"),
        IPort(name="axis2", label="Axis to swap", signature="basic:Integer"),
        IPort(name="ndarray", label="ndarray to swap the axes of",
              signature="basic:List"),
                    ]
    _output_ports = [
        OPort(name="swapped_ndarray", signature="basic:List"),
                    ]
    def compute(self):
        axis1 = self.get_input("axis1")
        axis2 = self.get_input("axis2")
        ndarray = self.get_input("ndarray")
        swapped_ndarray = np.swapaxes(ndarray, axis1, axis2)
        self.set_output("swapped_ndarray", swapped_ndarray)

# Defining the module names
_modules = [SpecFile, SpecScan, SpecMetadata, ImageStackImageSelector, \
            ImageStackSum, SpecFileProcessor, SpecFileParams, \
            Gridder, GridderParams, PlotGridded, SwapAxes
            ]
