import sys
from PyQt4 import QtGui

from interface import tabbed_widget, table_display
from data.couch_backend import CouchBackend
from data.util import Field

if __name__ == '__main__':
    job_fields = (
        Field('Name', str),
        Field('Specialties', list),
        Field('GRE General', bool),
    )
    job_backend = CouchBackend('jobs')
    
    school_fields = (
        Field('Name', str),
        Field('City', str),
    )
    school_backend = CouchBackend('schools')
    
    app = QtGui.QApplication(sys.argv)
    
    jobs = table_display.TableDisplay(job_fields, job_backend)
    schools = table_display.TableDisplay(school_fields, school_backend)
    
    td = tabbed_widget.TabbedWidget()
    td.addTab(jobs, 'Jobs')
    td.addTab(schools, 'Schools')
    td.show()
    
    sys.exit(app.exec_())
    