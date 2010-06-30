import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
sys.path.append('../data/')
from couch_backend import CouchBackend
from convert import InputDialog

ICON_DIR = '../icons/'

class TableDisplay(QtGui.QMainWindow):
    def __init__(self, fields, backend, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Data Display')
        
        self.fields = fields
        self.backend = backend
        
        self.create_table_model()
        self.create_toolbar()
        self.create_layout()
        
    def create_table_model(self):
        self.table_model = QtGui.QStandardItemModel(0, len(self.fields))
        headers = QtCore.QStringList([x.name for x in self.fields])
        self.table_model.setHorizontalHeaderLabels(headers)
        
        data = self.backend.get_data(self.fields)
        for row in data:
            items = map(QtGui.QStandardItem, row)
            map(lambda x: x.setEditable(False), items)
            self.table_model.appendRow(items)
    
    def create_toolbar(self):
        create = QtGui.QAction(QtGui.QIcon(ICON_DIR + 'new.png'), 'New', self)
        create.setShortcut('Ctrl+N')
        self.connect(create, QtCore.SIGNAL('triggered()'), self.new_dialog)
        
        edit = QtGui.QAction(QtGui.QIcon(ICON_DIR + 'edit.png'), 'Edit', self)
        edit.setShortcut('Ctrl+E')
        self.connect(edit, QtCore.SIGNAL('triggered()'), self.edit_dialog)

        self.toolbar = self.addToolBar('Modify')
        self.toolbar.addAction(create)
        self.toolbar.addAction(edit)
    
    def create_layout(self):
        self.table_view = QtGui.QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        
        self.mainLayout = QtGui.QVBoxLayout()
        self.setCentralWidget(self.table_view)
    
    def new_dialog(self):
        dialog = InputDialog(self.fields, self.backend, parent=self)
        data = []
        dialog.set_data(data)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            items = self.items_to_model(data)
            self.table_model.appendRow(items)
    
    def edit_dialog(self):
        row_list = self.table_view.selectionModel().selectedRows()
        try:
            row_num = row_list[0].row()
        except IndexError:
            return
        
        col_count = self.table_model.columnCount()
        row = [self.table_model.item(row_num, i) for i in range(col_count)]
        data = map(lambda x: x.data(role=QtCore.Qt.DisplayRole).toString(), row)
        
        dialog = InputDialog(self.fields, self.backend, parent=self)
        dialog.set_data(data)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            self.recycle_row(row_num)
    
    def recycle_row(self, row_num):
        old = self.table_model.takeRow(row_num)
        name = old[0].data(role=QtCore.Qt.DisplayRole).toString()
        raw_items = self.backend.get_row_by_id(str(name), self.fields)
        items = self.items_to_model(raw_items)
        self.table_model.insertRow(row_num, items)
    
    def items_to_model(self, raw_items):
        items = map(QtGui.QStandardItem, [str(x) for x in raw_items])
        map(lambda x: x.setEditable(False), items)
        return items
        

class Field:
    def __init__(self, name, data_type):
        self.name = name
        self.type = data_type

def main():
        job_fields = (
            Field('Name', str),
            Field('Specialties', list),
            Field('GRE General', bool),
        )
        backend = CouchBackend('data')
        
        app = QtGui.QApplication(sys.argv)
        icon = TableDisplay(job_fields, backend)
        icon.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
        main()
