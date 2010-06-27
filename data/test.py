import couchdb
couch = couchdb.Server()
print couch
db = couch.create('test')
print db
db['foo'] = {'bar': 'test'}
db['foo2'] = {'bar2': 'test2'}
print db['foo']

map_fun = '''function(doc) {
  if (doc.bar == 'test')
    emit(doc.bar, null);
}'''
for row in db.query(map_fun):
    print row.key

doc = db['foo']
db.delete(doc)
couch.delete('test') 
