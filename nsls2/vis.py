'''
Created on Apr 29, 2014

@author: edill
'''
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
from vistools.qt_widgets import CrossSectionMainWindow, Stack1DMainWindow
import numpy as np


class DataGen(Module):
    _settings = ModuleSettings(namespace="nsls2|vis|test")
    _input_ports = [
        IPort(name="num_datasets", label="Number of datasets to generate",
              signature="basic:Integer"),
    ]

    _output_ports = [
        OPort(name="OneDimStack", signature="basic:List"),
        OPort(name="TwoDimStack", signature="basic:List"),
        OPort(name="DataLabels", signature="basic:List"),
    ]

    def compute(self):
        length = self.get_input("num_datasets")
        self.set_output("OneDimStack", self.make_onedim(length))
        self.set_output("TwoDimStack", self.make_twodim(length))
        self.set_output("DataLabels", self.make_labels(length))

    def make_onedim(self, length):
        """
        Construct a one dimensional stack of height 'length'

        Parameters
        ----------
        length : int
            number of datasets to generate

        Returns
        -------
        data : list
            list of 2d np.ndarray
        """
        x_axis = np.arange(0, 25, .01)
        data = []
        for idx in range(length):
            x = x_axis
            y = np.sin(x_axis + idx)
            data.append((x, y))

        return data

    def make_twodim(self, length):
        """
        Construct a two dimensional stack of height 'length'

        Parameters
        ----------
        length : int
            number of datasets to generate

        Returns
        -------
        data : list
            list of 2d np.ndarray
        """
        x, y = [_ * 2 * np.pi / 500 for _ in np.ogrid[-500:500, -500:500]]
        rep = int(np.sqrt(length))
        data = []
        for idx in range(length):
            kx = idx // rep + 1
            ky = idx % rep
            data.append(np.sin(kx * x) * np.cos(ky * y) + 1.05)

        return data

    def make_labels(self, length):
        return [str(_) for _ in range(length)]


class CrossSectionCell(SpreadsheetCell):
    _settings = ModuleSettings(namespace="nsls2|vis")
    _input_ports = [
        IPort(name="data", label="Data to display",signature="basic:List"),
        IPort(name="keys", label="Names of the data",signature="basic:List"),
    ]

    _output_ports = [
        OPort(name="displayed_data", signature="basic:List"),
    ]

    def compute(self):
        data = self.get_input("data")
        keys = self.get_input("keys")
        self.cellWidget = self.displayAndWait(CrossSectionWidget, (data,keys,))


class CrossSectionWidget(QCellWidget):

    def __init__(self, parent=None):
        super(CrossSectionWidget, self).__init__(parent=parent)

    def updateContents(self, input_ports):
        (data,keys) = input_ports
        layout = QtGui.QHBoxLayout()
        widg = CrossSectionMainWindow(data_list=data, key_list=keys)
        layout.addWidget(widg)
        self.setLayout(layout)
        QCellWidget.updateContents(self, input_ports)


class Stack1DCell(SpreadsheetCell):
    _settings = ModuleSettings(namespace="nsls2|vis")
    _input_ports = [
        IPort(name="data", label="Data to display",signature="basic:List"),
        IPort(name="keys", label="Names of the data",signature="basic:List"),
    ]

    _output_ports = [
        OPort(name="displayed_data", signature="basic:List"),
    ]

    def compute(self):
        data = self.get_input("data")
        print("got data")
        keys = self.get_input("keys")
        print("got the keys")
        self.cellWidget = self.displayAndWait(Stack1DWidget, (data,keys,))


class Stack1DWidget(QCellWidget):

    def __init__(self, parent=None):
        super(Stack1DWidget, self).__init__(parent=parent)

    def updateContents(self, input_ports):
        (data,keys) = input_ports
        print("got data and keys")
        layout = QtGui.QHBoxLayout()
        print("declared the layout")
        widg = Stack1DMainWindow(data_list=data, key_list=keys)
        print("declared the stack1Dmainwindow")
        layout.addWidget(widg)
        print("added the widget to the layout")
        self.setLayout(layout)
        print("set the layout")
        QCellWidget.updateContents(self, input_ports)



#modules = [CrossSectionCell, Stack1DCell, DataGen]


def vistrails_modules():
    return [CrossSectionCell, Stack1DCell, DataGen]