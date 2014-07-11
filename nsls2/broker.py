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
from metadataStore.userapi.commands import search


class BrokerQuery(Module):
    _settings = ModuleSettings(namespace="nsls2|io")

    _input_ports = [
        IPort(name="query_dict", label="Query for the data broker",
              signature="basic:Dictionary")
    ]

    _output_ports = [
        OPort(name="query_result", signature="basic:Dictionary")
    ]

    def compute(self):
        query = self.get_input("query_dict")
        result = search(**query)
        self.set_output("query_result", result)


def vistrails_modules():
    return [BrokerQuery]