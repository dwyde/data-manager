import sys
from PyQt4 import QtGui

from interface.tabbed_widget import TabbedWidget
from interface.table_display import TableDisplay
from data.couch_backend import CouchBackend
from data.util import Field

# Define fields, for both the displays and the database.
school_fields = (
    Field('Name', str),
    Field('Specialties', list),
    Field('Deadline', str),
    Field('Recs', int),
    Field('GRE General', bool),
    Field('GRE Subject', bool),
    Field('US News Rank', int),
)

job_fields = (
    Field('Name', str),
    Field('Locations', list),
    Field('Deadline', str),
    Field('Contact', str),
)

# Run the application
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    school_backend = CouchBackend('schools')
    job_backend = CouchBackend('jobs')
    
    jobs = TableDisplay(job_fields, job_backend)
    schools = TableDisplay(school_fields, school_backend)
    
    td = TabbedWidget()
    td.addTab(schools, 'Schools')
    td.addTab(jobs, 'Jobs')
    td.show()
    
    sys.exit(app.exec_())
    