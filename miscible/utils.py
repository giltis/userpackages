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
from vistrails import api
print("vistrails api import successful")
from logging import Handler
print("logging Handler import successful")
from vistools.qt_widgets import query_widget
print("vistools qt_widgets query_widget import successful")
from .broker import search_keys_dict
print("search_keys_dict import successful")
print(search_keys_dict)
from .broker import search
print("search import successful")
import logging
print("logging import successful")
logger = logging.getLogger(__name__)
print("logger defined")


def search_databroker(search_dict):
    print("search: {0}".format(search_dict))
    result=search(**search_dict)
    print("result: {0}".format(result))
    return result

print("search_databroker function defined")
query_window = query_widget.QueryMainWindow(keys=search_keys_dict,
                                            search_func=search_databroker)

print("query_window initialized")

def setup_bnl_menu():
    """
    Creates and hooks up a BNL specific menu in the main window
    """
    print("in setup_bnl_menu")
    bw = api.get_builder_window()
    print("builder window obtained")
    # grab the menu bar
    menu_bar = bw.menuBar()
    print("menu bar obtained")

    bnl_menu = menu_bar.addMenu("BNL")
    print("bnl menu added")
    def foo():
        query_window.show()
    print("foo defined")
    bnl_menu.addAction("demo", foo)
    print("foo added to menu")

class ForwardingHandler(Handler):
    """

    This Handler forwards all records on to some other logger.  This is
    useful when integrating with an existing libraries/programs/GUIs
    that make use of logging.  This allows messages to hop between logger
    trees to either capture logging or inject messages into other handlers.

    Parameters
    ----------
    other_logger : logging.Logger
        The logger to forward
    """
    def __init__(self, other_logger):
        Handler.__init__(self)
        self._other_logger = other_logger

    def emit(self, record):
        self._other_logger.handle(record)
