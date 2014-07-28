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
from vistools.qt_widgets import CrossSectionMainWindow, Stack1DMainWindow
import numpy as np
from metadataStore.userapi.commands import search


class BrokerQuery(Module):
    _settings = ModuleSettings(namespace="NSLS2|io",
                               configure_widget=
                               "vis:NestedDictConfigurationWidget")

    _input_ports = [
        IPort(name="query_dict", label="Query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="complete_record", label="Return the complete record",
              signature="basic:Boolean", default=True)
    ]

    _output_ports = [
        OPort(name="query_result", signature="basic:List")
    ]

    def compute(self):
        query = self.get_input("query_dict")
        complete = self.get_input("complete_record")
        query["contents"] = complete
        result = search(**query)
        self.set_output("query_result", result)


def vistrails_modules():
    return [BrokerQuery]