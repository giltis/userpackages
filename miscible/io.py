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
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
from pims.extern.tifffile import imread
from nsls2.io.binary import read_binary

import logging
logger = logging.getLogger(__name__)


class ReadTiff(Module):
    _settings = ModuleSettings(namespace="io")

    _input_ports = [
        IPort(name="files", label="List of files",
              signature="basic:List"),
    ]

    _output_ports = [
        OPort(name="data", signature="basic:List")
    ]

    def compute(self):
        files_list = self.get_input("files")
        data_list = []
        for file in files_list:
            data_list.append(imread(file))
        self.set_output("data", data_list)


class ReadBinary(Module):
    _settings = ModuleSettings(namespace="io")

    _input_ports = [
        IPort(name="files", label="List of files", signature="basic:List"),
        IPort(name="params_dict", label="Dict of params",
              signature="basic:Dictionary"),
        IPort(name="nx", label="number of elements in x",
              signature="basic:Integer"),
        IPort(name="ny", label="number of elements in y",
              signature="basic:Integer"),
        IPort(name="nz", label="number of elements in z",
              signature="basic:Integer"),
        IPort(name="dsize", label="Numpy type of data elements",
              signature="basic:String"),
        IPort(name="headersize", label="size of file header in bytes",
              signature="basic:Integer"),
    ]

    _output_ports = [
        OPort(name="data", signature="basic:List")
    ]

    def compute(self):
        files_list = self.get_input("files")
        try:
            params_dict = self.get_input("params_dict")
        except ModuleError:
            params_dict = self._gather_input()

        data = []
        print(files_list)
        for _file in files_list:
            print(_file)
            data.append(read_binary(filename=_file, **params_dict))
        self.set_output("data", data)

    def _gather_input(self):
        """
        Parse the input ports

        Returns
        -------
        params_dict : dict
            Dictionary of parameters
        """

        params_dict = {}
        params_dict["nx"] = self.get_input("nx")
        params_dict["ny"] = self.get_input("ny")
        params_dict["nz"] = self.get_input("nz")
        params_dict["dsize"] = self.get_input("dsize")
        params_dict["headersize"] = self.get_input("headersize")

        return params_dict


def vistrails_modules():
    return [ReadTiff, ReadBinary]
