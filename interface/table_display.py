'''Display, edit, or add to a list view of items.'''

from PyQt4 import QtGui, QtCore
from interface import NEW_DIALOG, EDIT_DIALOG
from couch_backend import CouchBackend
from dialog import InputDialog

ICON_DIR = 'icons/'

class TableDisplay(QtGui.QMainWindow):
    '''
    Display a list of entries.
    '''
    
    def __init__(self, fields, backend, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
        self.fields = fields
        self.backend = backend
        
        self.create_table_model()
        self.create_toolbar()
        self.create_layout()
        
    def create_table_model(self):
        '''Build a model for a table view, from existing entries.'''
        
        self.table_model = QtGui.QStandardItemModel(0, len(self.fields))
        headers = QtCore.QStringList([x.name for x in self.fields])
        self.table_model.setHorizontalHeaderLabels(headers)
        
        data = self.backend.get_data(self.fields)
        for row in data:
            items = map(QtGui.QStandardItem, row)
            map(lambda x: x.setEditable(False), items)
            self.table_model.appendRow(items)
    
    def create_toolbar(self):
        '''Display a toolbar of action buttons.'''
        
        create = QtGui.QAction(QtGui.QIcon(ICON_DIR + 'new.png'), 'New', self)
        create.setShortcut('Ctrl+N')
        self.connect(create, QtCore.SIGNAL('triggered()'), self.new_dialog)
        
        edit = QtGui.QAction(QtGui.QIcon(ICON_DIR + 'edit.png'), 'Edit', self)
        edit.setShortcut('Ctrl+E')
        self.connect(edit, QtCore.SIGNAL('triggered()'), self.edit_dialog)
        
        delete = QtGui.QAction(QtGui.QIcon(ICON_DIR + 'delete.png'), 'Delete', self)
        delete.setShortcut('Delete')
        self.connect(delete, QtCore.SIGNAL('triggered()'), self.delete_dialog)

        self.toolbar = self.addToolBar('Modify')
        self.toolbar.addAction(create)
        self.toolbar.addAction(edit)
        self.toolbar.addAction(delete)
    
    def create_layout(self):
        '''Initialize a view for an existing table model.'''
        
        self.table_view = QtGui.QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setCentralWidget(self.table_view)
    
    def new_dialog(self):
        '''
        Display a dialog for adding a new row.
        Values from a newly-created row are put into the "data" variable.
        Perhaps this is a hack, but it seems to work okay.
        '''
        
        dialog = InputDialog(NEW_DIALOG, self.fields, self.backend, parent=self)
        data = [] # Pass a created row back through this variable
        dialog.set_data(data)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            items = self.items_to_model(data)
            self.table_model.appendRow(items)
    
    def edit_dialog(self):
        '''A dialog for editing an existing row.'''
        
        # Check that a row is highlighted
        row_num = self.current_row_num()
        if row_num == None:
            return
        
        # Get a highlighted row's values as a list of strings.
        col_count = self.table_model.columnCount()
        row = [self.table_model.item(row_num, i) for i in range(col_count)]
        data = map(lambda x: x.data(role=QtCore.Qt.DisplayRole).toString(), row)
        
        # Create and display an edit dialog.
        dialog = InputDialog(EDIT_DIALOG, self.fields, self.backend, parent=self)
        dialog.set_data(data)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            self.recycle_row(row_num)
    
    def delete_dialog(self):
        '''Delete the current row, if given user approval.'''
        
        row_num = self.current_row_num()
        if row_num == None:
            return
        
        reply = QtGui.QMessageBox.question(self, 'Delete entry?',
            'Are you sure that you want to delete the highlighted row?', 
            QtGui.QMessageBox.No|QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            # Go ahead and delete
            id_field = self.table_model.item(row_num, 0)
            name = id_field.data(role=QtCore.Qt.DisplayRole).toString()
            self.backend.delete_by_id(str(name))
            
            # Remove row from the table model and view
            self.table_model.takeRow(row_num)
    
    def recycle_row(self, row_num):
        '''
        Remove an old row and replace it with a freshly-edited version.
        The "Name" (ID) field cannot be edited, or else this would be harder.
        @param row_num: An index of the modified row.
        '''
        
        # Remove the current row
        old = self.table_model.takeRow(row_num)[0]
        
        # Replace it with the updated data.
        name = old.data(role=QtCore.Qt.DisplayRole).toString()
        raw_items = self.backend.get_row_by_id(str(name), self.fields)
        items = self.items_to_model(raw_items)
        self.table_model.insertRow(row_num, items)
    
    def items_to_model(self, raw_items):
        '''Prepare data of various types for life as a row in a table model.'''
        
        items = map(QtGui.QStandardItem, [str(x) for x in raw_items])
        map(lambda x: x.setEditable(False), items)
        return items
    
    def current_row_num(self):
        '''
        Get the index of the currently-selected row.
        @return: The index of the current row, or "None" if nothing is selected.
        '''
        row_list = self.table_view.selectionModel().selectedRows()
        try:
            return row_list[0].row()
        except IndexError:
            return None
    