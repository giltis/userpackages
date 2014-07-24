from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from vistrails import api

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
