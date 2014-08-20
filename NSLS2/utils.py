from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from vistrails import api

from logging import Handler
from vistools.qt_widgets import query_widget

query_window = query_widget.QueryMainWindow(keys=['a', 'b'])


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
