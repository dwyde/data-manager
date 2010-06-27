import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
sys.path.append('../data/')
from couch_backend import CouchBackend

class TableDisplay(QtGui.QWidget):
    def __init__(self, fields, backend, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Data Display')
        
        self.fields = fields
        self.backend = backend
        self.create_table()
        
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.table_view)
        self.setLayout(self.mainLayout)
        
    def create_table(self):
        self.table_model = QtGui.QStandardItemModel(0, len(self.fields))
        headers = QtCore.QStringList([x[0] for x in self.fields])
        self.table_model.setHorizontalHeaderLabels(headers)
        
        data = self.backend.get_data(self.fields)
        for row in data:
            items = map(QtGui.QStandardItem, row)
            map(lambda x: x.setEditable(False), items)
            self.table_model.appendRow(items)
        
        self.table_view = QtGui.QTableView()
        self.table_view.setModel(self.table_model)

def main():
        job_fields = (
            ('Name', str),
            ('Specialties', list),
            ('GRE General', bool),
        )
        backend = CouchBackend('data')
        
        app = QtGui.QApplication(sys.argv)
        icon = TableDisplay(job_fields, backend)
        icon.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
        main()
