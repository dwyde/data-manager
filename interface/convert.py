import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
sys.path.append('../data/')
from couch_backend import backend_save


class InputDialog(QtGui.QDialog):
    field_dict = {
        str: QtGui.QLineEdit,
        list: QtGui.QTextEdit,
        bool: QtGui.QRadioButton,
    }
    
    getters = {
        QtGui.QLineEdit : 'displayText',
        QtGui.QTextEdit : 'toPlainText',
        QtGui.QRadioButton : 'isChecked',
    }
    
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('New Entry')
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.data = {}
        
    def fields_to_qt(self, fields):
        self.formLayout = QtGui.QFormLayout()
        for name, field_type in fields:
            widget = self.field_dict[field_type]()
            self.formLayout.addRow(name, widget)
            self.data[name] = widget
        self.mainLayout.addLayout(self.formLayout)
        self.add_buttons()
    
    def add_buttons(self):
        ok = QtGui.QPushButton('OK')
        cancel = QtGui.QPushButton('Cancel')

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok)
        hbox.addWidget(cancel)
        
        self.mainLayout.addLayout(hbox)
        self.connect(ok, QtCore.SIGNAL('clicked()'), self.save_data)
        self.connect(cancel, QtCore.SIGNAL('clicked()'), self.close)
    
    def save_data(self):
        data = {}
        for k, v in self.data.iteritems():
            method = getattr(v, self.getters[type(v)])
            data[k] = method()
        print data
        backend_save(data)
        self.close()

def main():
        job_fields = (
            ('Name', str), 
            ('Specialties', list),
            ('GRE General', bool),
        )
        app = QtGui.QApplication(sys.argv)
        icon = InputDialog()
        icon.fields_to_qt(job_fields)
        icon.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
        main()
 