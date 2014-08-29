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
from .broker import search_keys_dict
print(search_keys_dict)
from .broker import search
from metadataStore.analysisapi.utility import listify, get_data_keys
import logging
logger = logging.getLogger(__name__)
from vistrails import api


def add_query_and_listify_to_canvas(query_dict, unique_query_dict,
                                    single_result):

    # get the controller (will be needed to change the module names
    controller = api.get_current_controller()

    mod_ids = []
    conn_ids = []
    # add the search dictionary to the canvas
    mod_dict_search = api.add_module(-100, 0, 'org.vistrails.vistrails.basic',
                                     'Dictionary', '')
    api.change_parameter(mod_dict_search.id, 'value', [query_dict])
    mod_ids.append(mod_dict_search.id)

    # add the unique search dictionary to the canvas
    mod_dict_unique = api.add_module(200, 0, 'org.vistrails.vistrails.basic',
                                     'Dictionary','')
    api.change_parameter(mod_dict_unique.id, 'value', [unique_query_dict])
    mod_ids.append(mod_dict_unique.id)

    # add the broker module to the canvas
    mod_broker = api.add_module(0, -100, 'org.vistrails.vistrails.NSLS2',
                                'BrokerQuery', 'broker')
    mod_ids.append(mod_broker.id)

    # connect the search dict and unique search dict to the broker module
    conn_ids.append(api.add_connection(mod_dict_search.id, 'value',
                                       mod_broker.id, 'query_dict').id)
    conn_ids.append(api.add_connection(mod_dict_unique.id, 'value',
                                       mod_broker.id, 'unique_query_dict').id)

    # get the datakeys from the run header
    data_keys = get_data_keys(single_result)
    horz_offset = 250
    vert_offset = -300
    index = 0
    for key in data_keys:
        print(key)
        # add the vistrails module for the listify key
        mod_key = api.add_module(horz_offset * index, vert_offset+100,
                                 'org.vistrails.vistrails.basic', 'String', '')
        mod_ids.append(mod_key.id)
        # set the parameter of the listify key module to be 'key'
        api.change_parameter(mod_key.id, 'value', [key])
        # change the module name
        controller.add_annotation(('__desc__', key), mod_key.id)
        controller.current_pipeline_scene.recreate_module(
            controller.current_pipeline, mod_key.id)
        # add the vistrails module for the listify operation
        mod_listify = api.add_module(horz_offset * index, vert_offset,
                                     'org.vistrails.vistrails.NSLS2',
                                     'Listify', 'broker')
        mod_ids.append(mod_listify.id)
        # set the parameter of the listify to key

        # connect the listify key to the listify module
        conn_ids.append(api.add_connection(mod_key.id, 'value', mod_listify.id,
                                           'data_keys').id)

        # connect the broker result to the listify module
        conn_ids.append(api.add_connection(mod_broker.id, 'query_result',
                                           mod_listify.id, 'run_header').id)
        # if this is the first key, add the time list module
        if index == 0:
            mod_time = api.add_module(-200, vert_offset-100,
                                      'org.vistrails.vistrails.basic', 'List', '')
            conn_ids.append(api.add_connection(mod_listify.id,
                                               'listified_time', mod_time.id,
                                               'value').id)
            controller.add_annotation(('__desc__', 'time'), mod_time.id)
            controller.current_pipeline_scene.recreate_module(
                controller.current_pipeline, mod_time.id)

        mod_data = api.add_module(horz_offset * index, vert_offset-100,
                                  'org.vistrails.vistrails.basic', 'List', '')
        conn_ids.append(api.add_connection(mod_listify.id, 'listified_data',
                                           mod_data.id, 'value').id)
        controller.add_annotation(('__desc__', (key+"_data")), mod_data.id)
        controller.current_pipeline_scene.recreate_module(
            controller.current_pipeline, mod_data.id)
        index += 1

    # annotate the modules
    controller.add_annotation(('__desc__', 'search dictionary'),
                              mod_dict_search.id)
    controller.current_pipeline_scene.recreate_module(
        controller.current_pipeline, mod_dict_search.id)

    controller.add_annotation(('__desc__',
                               'guaranteed unique search dictionary'),
                              mod_dict_unique.id)
    controller.current_pipeline_scene.recreate_module(
        controller.current_pipeline, mod_dict_unique.id)
    print("mod_ids: {0}".format(mod_ids))
    print("conn_ids: {0}".format(conn_ids))
    group = api.create_group(mod_ids, conn_ids)
    print("group class: {0}".format(group.__class__))

    controller.add_annotation(('__desc__', 'Broker Search Group'), group.id)
    controller.current_pipeline_scene.recreate_module(
        controller.current_pipeline, group.id)


def gen_unique_id(run_header):
    """
    Create a unique search dictionary from the run header that gets fed in.

    Parameters
    ----------
    run_header : dict
        The run header that gets returned by the data broker

    Returns
    -------
    dict
        Search dictionary that, when unpacked into
        metadataStore.userapi.commands.search will guarantee that a single run
        header is returned
    """
    print("run_header.__class__: {0}".format(run_header.__class__))
    print("run_header: {0}".format(run_header))
    return {"_id": run_header["_id"]}


def search_databroker(search_dict):
    """
    Function that gets fed to the query widget which gets executed when the
    'search' button is pressed

    Parameters
    ----------
    search_dict : dict
        Dictionary which has k:v pairs that
        metadataStore.userapi.commands.search understands

    Returns
    -------
    dict
        Dictionary of run headers that get returned by the data broker
    """
    result=search(**search_dict)
    return result


query_window = query_widget.QueryMainWindow(keys=search_keys_dict,
                                            search_func=search_databroker,
                                            add_func=add_query_and_listify_to_canvas,
                                            unique_id_func=gen_unique_id)


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
