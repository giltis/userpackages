'''
Created on Apr 29, 2014

@author: edill
'''
from PyQt4 import QtCore, QtGui
from vistrails.core.modules.vistrails_module import Module
from vistrails.core.modules.config import IPort, OPort
from vistrails.packages.spreadsheet.basic_widgets import SpreadsheetCell
from vistrails.packages.spreadsheet.spreadsheet_cell import QCellWidget
from vistools.qt_widgets import StackScanner
#------------------------------------------ from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas  # noqa


class StackScannerCell(SpreadsheetCell):
    _input_ports = [
        IPort(name="img_stack", label="Stack of images to display", \
              signature="basic:List"),
        ]
    
    _output_ports = [
        OPort(name="arr_2d", signature="basic:List"),
        ]
    
    def compute(self):
        img_stack = self.get_input("img_stack")
        self.cellWidget = self.displayAndWait(StackScannerCellWidget, (img_stack,))
    
    def set_out_arr(self, arr_2d):
        self.set_output("arr_2d", arr_2d)

class StackScannerCellWidget(QCellWidget):
    
    def __init__(self, parent=None):
        QCellWidget.__init__(self,parent)
        self._stack_scanner = None
        
    def updateContents(self, inputPorts):
        """ updateContents(inputPorts: tuple) -> None
        Update the widget contents based on the input data
        
        """
        (img_stack, ) = inputPorts
        if img_stack is not None:
            if self._stack_scanner is None:
                self._stack_scanner = StackScanner(img_stack)
                hbox = QtGui.QHBoxLayout()
                hbox.addWidget(self._stack_scanner)
                self.setLayout(hbox)
            else:
                self._stack_scanner.set_img_stack(img_stack)
                
        else:
            self.label.setText("Invalid image stack file!")

        QCellWidget.updateContents(self, inputPorts)
    
    #===========================================================================
    # def clearLayout(self, layout):
    #     if layout is not None:
    #         while layout.count():
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.deleteLater()
    #             else:
    #                 self.clearLayout(item.layout())
    #===========================================================================

_modules = [StackScannerCell]