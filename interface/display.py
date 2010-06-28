import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
sys.path.append('../data/')
from couch_backend import CouchBackend
from convert import InputDialog

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
        create = QtGui.QAction(QtGui.QIcon('icons/new.png'), 'New', self)
        create.setShortcut('Ctrl+N')
        self.connect(create, QtCore.SIGNAL('triggered()'), self.new_dialog)
        
        edit = QtGui.QAction(QtGui.QIcon('icons/edit.png'), 'Edit', self)
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
        #self.mainLayout.addWidget(self.toolbar)
        #self.setLayout(self.mainLayout)
    
    def new_dialog(self):
        dialog = InputDialog(self.fields, self.backend, parent=self)
        dialog.set_data(None)
        dialog.show()
    
    def edit_dialog(self):
        row_list = self.table_view.selectionModel().selectedRows()
        row_num = row_list[0].row()
        row = self.table_model.takeRow(row_num)
        data = map(lambda x: x.data(role=QtCore.Qt.DisplayRole).toString(), row)
        print data
        
        dialog = InputDialog(self.fields, self.backend, parent=self)
        dialog.set_data(data)
        dialog.show()

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
