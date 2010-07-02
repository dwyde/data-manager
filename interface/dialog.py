from PyQt4 import QtGui
from PyQt4 import QtCore
from couch_backend import CouchBackend

class QWidgetMethods:
    pass

class QLineEditMethods(QWidgetMethods):
    def get(self, widget):
        return widget.displayText()
    
    def set(self, widget, value):
        widget.setText(value)

class QTextEditMethods(QWidgetMethods):
    def get(self, widget):
        return widget.toPlainText()
        
    def set(self, widget, value):
        map(widget.append, value.split('\n'))
    
class QCheckBoxMethods(QWidgetMethods):
    def get(self, widget):
        return widget.isChecked()
        
    def set(self, widget, value):
        if value == 'True':
            tf = True
        else:
            tf = False
        widget.setChecked(tf)

class QSpinBoxMethods(QWidgetMethods):
    def get(self, widget):
        return widget.value()
        
    def set(self, widget, value):
        widget.setValue(widget.valueFromText(value))

class InputDialog(QtGui.QDialog):
    field_dict = {
        str: QtGui.QLineEdit,
        list: QtGui.QTextEdit,
        bool: QtGui.QCheckBox,
        int: QtGui.QSpinBox,
    }
    
    proxies = {
        QtGui.QLineEdit : QLineEditMethods(),
        QtGui.QTextEdit : QTextEditMethods(),
        QtGui.QCheckBox : QCheckBoxMethods(),
        QtGui.QSpinBox  : QSpinBoxMethods(),
    }
    
    def __init__(self, fields, backend, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('New Entry')
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.fields = fields
        self.backend = backend
    
    def set_data(self, data):
        # Save a reference to data, so we can pass back the ID of a new row
        self._old_data = data
        if data == []:
            self.defaults = ['' for x in self.fields]
        else:
            self.defaults = data
        
        self.fields_to_qt()
    
    def fields_to_qt(self):
        self.data = {}
        self.formLayout = QtGui.QFormLayout()
        for field, value in zip(self.fields, self.defaults):
            widget = self.field_dict[field.type]()
            self.proper_widget_value(widget, value)
            self.formLayout.addRow(field.name, widget)
            self.data[field.name] = widget
        
        # Edit dialogs cannot have their ID (name) changed.
        if self.defaults[0] != '': 
            self.formLayout.itemAt(1).widget().setReadOnly(True)
        self.mainLayout.addLayout(self.formLayout)
        self.add_buttons()
    
    def proper_widget_value(self, widget, value):
        methods = self.proxies[type(widget)]
        methods.set(widget, value)
    
    def add_buttons(self):
        ok = QtGui.QPushButton('OK')
        cancel = QtGui.QPushButton('Cancel')

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(ok)
        hbox.addWidget(cancel)
        
        self.mainLayout.addLayout(hbox)
        self.connect(ok, QtCore.SIGNAL('clicked()'), self.save_data)
        self.connect(cancel, QtCore.SIGNAL('clicked()'), self.reject)
    
    def qstring_to_str(self, value):
        vtype = type(value)
        if vtype == QtCore.QString:
            return str(value)
        elif vtype == QtCore.QStringList:
            return [str(x) for x in value]
        else:
            return value
    
    def save_data(self):
        if not self.has_id():
            return
        data = {}
        for name, widget in self.data.iteritems():
            methods = self.proxies[type(widget)]
            value = methods.get(widget)
            data[name] = self.qstring_to_str(value)
        if self._old_data == []:
            self._old_data.extend([data[f.name] for f in self.fields])
        self.backend.save(data)
        self.accept()

    def has_id(self):
        id_field = self.fields[0].name
        if self.data[id_field].displayText() == '':
            return False
        else:
            return True
