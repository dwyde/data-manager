'''A very basic "notebook" widget, with the capacity for multiple tabs.'''

from PyQt4 import QtGui

class TabbedWidget(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent) 
        
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Data Display')
        