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

from logging import Handler
from vistools.qt_widgets import query_widget
from .broker import search_keys_dict, search


def search_databroker(search_dict):
    print("search: {0}".format(search_dict))
    result=search(**search_dict)
    print("result: {0}".format(result))
    return result

query_window = query_widget.QueryMainWindow(keys=search_keys_dict,
                                            search_func=search_databroker)


def setup_bnl_menu():
    """
    Creates and hooks up a BNL specific menu in the main window
    """
    bw = api.get_builder_window()
    # grab the menu bar
    menu_bar = bw.menuBar()

    bnl_menu = menu_bar.addMenu("BNL")

    def foo():
        query_window.show()

    bnl_menu.addAction("demo", foo)


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
