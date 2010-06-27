import couchdb
from couchdb import Document
from couchdb.schema import *

class School(Document):
    name = TextField()
    specialties = ListField(TextField)
    gre_general = BooleanField()
    gre_subject = BooleanField()
    deadline = DateField()
    contact = TextField()
    rank = IntegerField()
    notes = ListField(TextField)

class Job(Document):
    name = TextField()
    location = TextField()
    deadline = DateField()
    contact = TextField()
    notes = ListField(TextField)

if __name__ == '__main__':
    couch = couchdb.Server()
    db = couch.create('test')
    #db = couch['test']
    s = School(name='Test', specialties=['science', 'math'], gre_general=True, gre_subject=False,
    deadline=None, rank=8) #id='unique'
    s.store(db)
    couch.delete('test')