'''
Display a dialog for adding new entries and editing existing ones.
'''

from PyQt4 import QtGui
from PyQt4 import QtCore
from interface import NEW_DIALOG, EDIT_DIALOG
from couch_backend import CouchBackend

# Widget wrappers: simplify getting and setting of values for different widgets.
class QLineEditWrap(QtGui.QLineEdit):
    '''A thin wrapper around a QLineEdit widget.'''
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
    
    def get(self):
        return self.displayText()
    
    def set(self, value):
        self.setText(value)

class QTextEditWrap(QtGui.QTextEdit):
    '''A thin wrapper around a QTextEdit widget.'''
    
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        
    def get(self):
        return self.toPlainText()
        
    def set(self, value):
        map(self.append, value.split('\n')) # Display newlines correctly
    
class QCheckBoxWrap(QtGui.QCheckBox):
    '''A thin wrapper around a QCheckBox widget.'''
    
    def __init__(self, parent=None):
        QtGui.QCheckBox.__init__(self, parent)
        
    def get(self):
        return self.isChecked()
        
    def set(self, value):
        if value == 'True':
            tf = True
        else:
            tf = False
        self.setChecked(tf)

class QSpinBoxWrap(QtGui.QSpinBox):
    '''A thin wrapper around a QSpinBox widget.'''
    
    def __init__(self, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        
    def get(self):
        return self.value()
        
    def set(self, value):
        self.setValue(self.valueFromText(value))

class InputDialog(QtGui.QDialog):
    '''A dialog for adding a new entry or editing an exisitng one.'''
    
    # Map storage data types to QtGui widgets.
    widgets = {
        str: QLineEditWrap,
        list: QTextEditWrap,
        bool: QCheckBoxWrap,
        int: QSpinBoxWrap,
    }
    
    def __init__(self, dialog_type, fields, backend, parent=None):
        '''
        Constructor for InputDialog class.
        @param dialog_type: 'NEW' or 'EDIT'
        @param fields: A tuple of objects mapping a field name to a Python data type
        @param backend: A database storage backend, such as CouchDB
        '''
        
        QtGui.QDialog.__init__(self, parent)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('New Entry')
        self.mainLayout = QtGui.QVBoxLayout()
        self.setLayout(self.mainLayout)
        
        self.type = dialog_type
        self.fields = fields
        self.backend = backend
    
    def set_data(self, data):
        '''
        Store a row of data for future editing, or fill in blanks.
        Save a reference to data, so we can pass back the ID of a new row
        @param data: A list of of values, corresponding to a row in the database
        '''
        
        if self.type == NEW_DIALOG:
            self.defaults = ['' for x in self.fields]
        else:
            self.defaults = data
        self._old_data = data
        
        self.fields_to_qt()
    
    def fields_to_qt(self):
        '''
        Create an appropriate widget for each defined data field.
        Add each widget to a QFormLayout, and store the values for later.
        '''
        
        self.data = {}
        self.formLayout = QtGui.QFormLayout()
        for field, value in zip(self.fields, self.defaults):
            widget = self.widgets[field.type]()
            widget.set(value)
            self.formLayout.addRow(field.name, widget)
            self.data[field.name] = widget
        
        # Edit dialogs cannot have their ID (name) changed.
        if self.type == EDIT_DIALOG: 
            self.formLayout.itemAt(1).widget().setReadOnly(True)
        self.mainLayout.addLayout(self.formLayout)
        self.add_buttons()
    
    def add_buttons(self):
        '''
        Insert buttons into the layout, to confirm or cancel changes.
        '''
        
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
        '''
        Convert a PyQt QString into a regular Python string, if applicable.
        @param value: A value that may or may not be a QString
        @return: An appropriately-typed value
        '''
        
        vtype = type(value)
        if vtype == QtCore.QString:
            return str(value)
        elif vtype == QtCore.QStringList:
            return [str(x) for x in value]
        else:
            return value
    
    def save_data(self):
        '''
        Store data from the dialog into a database backend.
        '''

        # Only accept if the ID field ("Name") is filled in.
        if not self.valid_id():
            return
        data = {}
        for name, widget in self.data.iteritems():
            value = widget.get()
            data[name] = self.qstring_to_str(value)
        
        # Pass old data back to the main program (it needs the original ID)
        self._old_data.extend([data[f.name] for f in self.fields])
        
        self.backend.save(data)
        self.accept()

    def valid_id(self):
        '''Determine if the ID (Name) field is filled in properly.'''
        
        id_field = self.fields[0].name
        name = self.data[id_field].displayText()
        row = self.backend.get_row_by_id(str(name), self.fields)
        if name == '':
            return False
        elif row != [] and self.type == NEW_DIALOG: # ID already in use
            QtGui.QMessageBox.question(self, 'Warning',
                    'That ID (%s) is already in use.' % self.fields[0].name)
        else:
            return True
