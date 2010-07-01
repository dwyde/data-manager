import couchdb
import re

class CouchBackend:
    '''
    Use CouchDB as a backend.
    Rely on the python-couchdb package for convenience.
    '''
    
    # Regular expressions to filter illegal characters out of CouchDB names.
    bad_dbname_chars = r'[^-_$()+/a-z0-9]'
    bad_docname_chars = r'\W'
    
    def __init__(self, dbname):
        '''
        Class constructor: store an active database for later use.
        @param dbname: A name for this database
        '''
        self.couch = couchdb.Server()
        name = self._safe_name(dbname, self.bad_dbname_chars)
        try:
            self.db = self.couch[name]
        except couchdb.client.ResourceNotFound:
            self.db = self.couch.create(name)
    
    def _safe_name(self, name, illegal_chars):
        '''
        Enforce a valid naming scheme for CouchDB objects.
        @param name: A string to be filtered
        @param illegal_chars: A regex of characters to be removed
        @return: A clean string
        '''
        
        return re.sub(illegal_chars, '', name)
    
    def save(self, data):
        '''
        Permanently store data into a CouchDB document.
        Overwrite a document with a conflicting name.
        @param data: A dictionary of key:value pairs, to be JSON-ized
        '''
        
        doc_id = self._safe_name(data['Name'], self.bad_docname_chars)
        try:
            del self.db[doc_id]
        except couchdb.client.ResourceNotFound:
            pass
        self.db[doc_id] = data
    
    def get_data(self, fields):
        '''
        Use a temporary view to obtain selected data from every document.
        @param fields: An n-tuple of data fields, names and associated types
        @return: One document at a time, with all values as strings
        '''
        
        for row in self.db.view('_all_docs', include_docs=True):
            data = [row.doc.get(f.name) for f in fields]
            yield map(str, data)
    
    def get_row_by_id(self, name, fields):
        '''
        Get selected data fields from a document.
        @param name: A unique name; "primary key" equivalent
        @param fields: An n-tuple of (field name, type) pairs
        @return: An ordered list of the requested fields
        '''
        
        safe = self._safe_name(name, self.bad_docname_chars)
        return [self.db[safe][f.name] for f in fields]
    
    def delete_by_id(self, name):
        '''
        Permanently remove a document from the database, if it exists.
        @param name: An ID of a document to be deleted
        '''
        
        safe = self._safe_name(name, self.bad_docname_chars)
        try:
            del self.db[safe]
        except couchdb.client.ResourceNotFound:
            pass