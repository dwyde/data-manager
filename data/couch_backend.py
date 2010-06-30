import couchdb
from couchdb import Document
from couchdb.schema import *
import re

class CouchBackend:
    bad_dbname_chars = r'[^-_$()+/a-z0-9]'
    bad_docname_chars = r'\W'
    
    def __init__(self, dbname):
        self.couch = couchdb.Server()
        name = self._safe_name(dbname, self.bad_dbname_chars)
        try:
            self.db = self.couch[name]
        except couchdb.client.ResourceNotFound:
            self.db = self.couch.create(name)
    
    def _safe_name(self, name, illegal_chars):
        return re.sub(illegal_chars, '', name)
    
    def save(self, data):
        doc_id = self._safe_name(data['Name'], self.bad_docname_chars)
        try:
            del self.db[doc_id]
        except couchdb.client.ResourceNotFound:
            pass
        self.db[doc_id] = data
    
    def get_data(self, fields):
        for row in self.db.view('_all_docs', include_docs=True):
            data = [row.doc.get(x.name) for x in fields]
            yield map(str, data)
    
    def get_row_by_id(self, name, fields):
        safe = self._safe_name(name, self.bad_docname_chars)
        return [self.db[safe][f.name] for f in fields]
    
    def delete_by_id(self, name):
        try:
            del self.db[name]
        except couchdb.client.ResourceNotFound:
            print 'Can\'t delete document with id "%s"' % (name,)