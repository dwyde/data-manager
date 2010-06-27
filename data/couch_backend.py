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
        self.db[doc_id] = data
        print self.db[doc_id]
    
    def get_data(self, fields):
        for row in self.db.view('_all_docs', include_docs=True):
            data = [row.doc.get(x[0]) for x in fields]
            yield map(str, data)
            