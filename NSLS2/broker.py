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

try:
    from metadataStore.userapi.commands import search
except ImportError:
    def search(*args, **kwargs):
        err_msg = "NSLS2 data broker is not importable. Search cannot proceed"
        print("userpackages/NSLS2/broker.py: {0}".format(err_msg))
        logger.warning(err_msg)
try:
    from metadataStore.userapi.commands import search_keys_dict
except ImportError:
    search_keys_dict = {"search_keys_dict": "Import Unsuccessful"}

class BrokerQuery(Module):
    _settings = ModuleSettings(namespace="NSLS2|io",
                               configure_widget=
                               "vis:NestedDictConfigurationWidget")

    _input_ports = [
        IPort(name="query_dict", label="Query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="is_returning_data", label="Return data with search results",
              signature="basic:Boolean", default=True)
    ]

    _output_ports = [
        OPort(name="query_result", signature="basic:List")
    ]

    def compute(self):
        query = self.get_input("query_dict")
        data = self.get_input("is_returning_data")
        query["data"] = data
        result = search(**query)
        self.set_output("query_result", result)


def vistrails_modules():
    return [BrokerQuery]