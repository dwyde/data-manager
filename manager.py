import sys
from PyQt4 import QtGui

from interface.tabbed_widget import TabbedWidget
from interface.table_display import TableDisplay
from data.couch_backend import CouchBackend
from data.util import Field

job_fields = (
    Field('Name', str),
    Field('Locations', list),
)

school_fields = (
    Field('Name', str),
    Field('Specialties', list),
    Field('Deadline', str),
    Field('US News Rank', int),
    Field('GRE General', bool),
    Field('GRE Subject', bool),
)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    job_backend = CouchBackend('jobs')
    school_backend = CouchBackend('schools')
    
    jobs = TableDisplay(job_fields, job_backend)
    schools = TableDisplay(school_fields, school_backend)
    
    td = TabbedWidget()
    td.addTab(jobs, 'Jobs')
    td.addTab(schools, 'Schools')
    td.show()
    
    sys.exit(app.exec_())
    