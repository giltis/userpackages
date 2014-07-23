'''
Created on Apr 29, 2014

@author: edill
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module, ModuleSettings
from vistrails.core.modules.config import IPort, OPort
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
from vistools.qt_widgets import CrossSectionMainWindow, Stack1DMainWindow, displaydict
import numpy as np
from vistrails.gui.modules.constant_configuration import ConstantEnumWidgetBase
from vistrails.gui.modules.module_configure import StandardModuleConfigurationWidget


class DataGen(Module):
    _settings = ModuleSettings(namespace="NSLS2|vis|test")
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
    _settings = ModuleSettings(namespace="NSLS2|vis")
    _input_ports = [
        IPort(name="data", label="Data to display",signature="basic:List"),
        IPort(name="keys", label="Names of the data",signature="basic:List"),
    ]

    _output_ports = [
        OPort(name="displayed_data", signature="basic:List"),
    ]

    def compute(self):
        data = self.get_input("data")
        try :
            keys = self.get_input("keys")
        except Exception:
            keys = range(len(data))
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
    _settings = ModuleSettings(namespace="NSLS2|vis")
    _input_ports = [
        IPort(name="data", label="Data to display",signature="basic:List"),
        IPort(name="keys", label="Names of the data",signature="basic:List"),
    ]

    _output_ports = [
        OPort(name="displayed_data", signature="basic:List"),
    ]

    def compute(self):
        data = self.get_input("data")
        try:
            keys = self.get_input("keys")
        except Exception:
            keys = range(len(data))
        self.cellWidget = self.displayAndWait(Stack1DWidget, (data,keys,))


class Stack1DWidget(QCellWidget):

    def __init__(self, parent=None):
        super(Stack1DWidget, self).__init__(parent=parent)

    def updateContents(self, input_ports):
        (data,keys) = input_ports
        layout = QtGui.QHBoxLayout()
        widg = Stack1DMainWindow(data_list=data, key_list=keys)
        layout.addWidget(widg)
        self.setLayout(layout)
        QCellWidget.updateContents(self, input_ports)


class NestedDictConfigurationWidget(StandardModuleConfigurationWidget):
    _settings = ModuleSettings(namespace="NSLS2|vis")

    def __init__(self, *args, **kwargs):
        super(NestedDictConfigurationWidget, self).__init__(*args, **kwargs)
        layout = QtGui.QVBoxLayout()
        self._query_widg = self.construct_query_widget()
        self._results_widg = self.construct_results_widget()

        layout.addWidget(self._query_widg)
        layout.addWidget(self._results_widg)

    def construct_query_widget(self):
        """
        Function that constructs and initializes the querying widget
        Returns
        -------
        query_widget : QWidget
        """
        _widg = QtGui.QWidget()

        return _widg

    def construct_results_widget(self):
        """
        Function that constructs and initializes the results widget

        Returns
        -------
        results_widget : QWidget
        """
        layout = QtGui.QHBoxLayout()
        _widg = displaydict.DisplayDict()
        layout.addWidget(_widg)
        self.setLayout(layout)
        return _widg


    def set_query(self, query):
        """
        Function that sets the query entries
        :param query:
        :return:
        """
        pass

    def set_results(self, results):
        """
        Function that sets the results

        Parameters
        ----------
        results : obj
            List, Dictionary or Object are all valid and will behave
            differently.
        """
        self._results_widg.set_tree(results)

    # Override functions
    def saveTriggered(self):
        pass

    def resetTriggered(self):
        pass


class NestedDictCell(SpreadsheetCell):
    _settings = ModuleSettings(namespace="NSLS2|vis")
    _input_ports = [
        IPort(name="dict_list", label="Dictionary to display",
              signature="basic:List"),
    ]

    def compute(self):
        dict_list = self.get_input("dict_list")
        self.cellWidget = self.displayAndWait(NestedDictWidget, (dict_list,))


class NestedDictWidget(QCellWidget):

    def __init__(self, parent=None):
        super(NestedDictWidget, self).__init__(parent=parent)

    def updateContents(self, input_ports):
        dict_list, = input_ports
        layout = QtGui.QHBoxLayout()
        widg = displaydict.DisplayDict()
        widg.set_tree(dict_list)
        layout.addWidget(widg)
        self.setLayout(layout)
        QCellWidget.updateContents(self, input_ports)


#modules = [CrossSectionCell, Stack1DCell, DataGen]


def vistrails_modules():
    return [CrossSectionCell, Stack1DCell, DataGen, NestedDictCell]
