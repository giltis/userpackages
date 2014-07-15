'''
Created on Apr 29, 2014

@author: edill
'''
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
from pims.extern.tifffile import imread
from nsls2.io.binary import read_binary

class ReadTiff(Module):
    _settings = ModuleSettings(namespace="NSLS2|io")

    _input_ports = [
        IPort(name="files", label="List of files",signature="basic:List"),
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
    _settings = ModuleSettings(namespace="NSLS2|io")

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
        except Exception:
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