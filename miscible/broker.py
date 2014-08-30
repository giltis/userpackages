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
import numpy as np
import logging
logger = logging.getLogger(__name__)

try:
    from metadataStore.userapi.commands import search
except ImportError:
    def search(*args, **kwargs):
        err_msg = ("search from metadataStore.userapi.commands is not "
                   "importable. Search cannot proceed")
        logger.warning(err_msg)
try:
    from metadataStore.userapi.commands import search_keys_dict
except ImportError:
    search_keys_dict = {"search_keys_dict": "Import Unsuccessful"}

try:
    from metadataStore.analysisapi.utility import listify
except ImportError:
    def listify(*args, **kwargs):
        err_msg = ("listify from metadataStore.analysis.utility is not "
                   "importable. run_header cannot be listified")
        logger.warning(err_msg)


class BrokerQuery(Module):
    _settings = ModuleSettings(namespace="broker")

    _input_ports = [
        IPort(name="unique_query_dict",
              label="guaranteed unique query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="query_dict", label="Query for the data broker",
              signature="basic:Dictionary"),
        IPort(name="is_returning_data", label="Return data with search results",
              signature="basic:Boolean", default=True)
    ]

    _output_ports = [
        OPort(name="query_result", signature="basic:Dictionary")
    ]

    def compute(self):
        query = None
        if self.has_input("query_dict"):
            query = self.get_input("query_dict")
            return_only_one = False
        if self.has_input("unique_query_dict"):
            query = self.get_input("unique_query_dict")
            return_only_one = True

        if query is None:
            logger.debug("no search dictionary was passed in, search "
                         "cannot proceed")
            return
        logger.debug("broker_query: {0}".format(query))
        data = self.get_input("is_returning_data")
        query["data"] = data
        result = search(**query)
        if return_only_one:
            keys = list(result)
            result = result[keys[0]]
        self.set_output("query_result", result)
        logger.debug("result: {0}".format(list(result)))


class Listify(Module):
    _settings = ModuleSettings(namespace="broker")

    _input_ports = [
        IPort(name="run_header",
              label="Run header from the data broker",
              signature="basic:Dictionary"),
        IPort(name="data_keys",
              label="The data key to turn in to a list",
              signature="basic:String"),
    ]

    _output_ports = [
        OPort(name="listified_data", signature="basic:List"),
        OPort(name="data_keys", signature="basic:List"),
        OPort(name="listified_time", signature="basic:List"),
    ]

    def compute(self):
        # gather input
        header = None
        if self.has_input("run_header"):
            header = self.get_input("run_header")
        if header is None:
            logger.debug("listify cannot do anything without a header")
            return

        key = None
        if self.has_input("data_keys"):
            key = self.get_input("data_keys")

        data_dict = listify(data_keys=key, run_header=header)
        # remove time from the dictionary
        time = data_dict.pop('time')
        # stringify the datetime object that gets returned
        time = [t.isoformat() for t in time]
        # get the remaining keys
        keys = list(data_dict)
        data = [data_dict[key] for key in keys]
        # check to see if data is a list of lists
        if len(data) == 1 and isinstance(data[0], list):
            data = data[0]
        # log the values set to the output ports at a debug level
        logger.debug('data ', data)
        logger.debug('keys ', keys)
        logger.debug('time ', time)
        # set the module's output
        self.set_output("data_keys", keys)
        self.set_output("listified_data", data)
        self.set_output("listified_time", time)


def vistrails_modules():
    return [BrokerQuery, Listify]
