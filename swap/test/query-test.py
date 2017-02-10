################################################################
# Test functions for query class

from swap.mongo.query import Query
from swap.mongo.query import Group

################################################################
# Limit
def test_limit():
    q = Query()
    q.limit(5)
    assert q._pipeline[-1] == {'$limit': 5}

################################################################
# Match
def test_match_eq():
    q = Query()
    q.match('key', 'value')
    assert q._pipeline[-1] == {'$match':{'key':'value'}}

def test_match_neq():
    q = Query()
    q.match('key', 'value', False)

    assert q._pipeline[-1] == {'$match':{'key':{'$ne':'value'}}}

################################################################
# Project
def test_add_new_field():
    q = Query()
    q.project([('name', 100)])

    assert q._pipeline[-1] == {'$project': \
        {'name': {'$literal': 100}}}

def test_project_str():
    q = Query()
    q.project('name')

    assert q._pipeline[-1] == {'$project': {'name': 1}}

def test_add_fields_list():
    q = Query()
    fields = ['field1', 'field2', 'field3']
    q.project(fields)

    assert q._pipeline[-1] == {'$project':{'field1':1,'field2':1,'field3':1}}

def test_add_fields_set():
    q = Query()
    fields = {'field1', 'field2', 'field3'}
    q.project(fields)

    assert q._pipeline[-1] == {'$project':{'field1':1,'field2':1,'field3':1}}

def test_add_fields_dict():
    q = Query()
    fields = {'field1':'$field1', 'field2':'$field2'}
    q.project(fields)

    assert q._pipeline[-1] == {'$project':fields}

################################################################
# Out

def test_out():
    q = Query()
    q.out('collection')

    assert q._pipeline[-1] == {'$out':'collection'}

################################################################
# Group

def test_group_str():
    q = Query()
    q.group("field")

    assert q._pipeline[-1] == {'$group':{"_id":"$field"}}

def test_group_list():
    q = Query()
    q.group(['field1','field2'])

    assert q._pipeline[-1] == {'$group':{'_id':{'field1':'$field1','field2':'$field2'}}}

def test_group_list():
    q = Query()
    q.group(['field1','field2'])

    assert q._pipeline[-1] == {'$group':{"_id":{'field1':'$field1','field2':'$field2'}}}

def test_group_count():
    q = Query()
    q.group('field',count=True)

    assert q._pipeline[-1] == {'$group':{'_id':'$field','count':{'$sum':1}}}

################################################################
# Group Class

def test_Group_str():
    g = Group().id('field')

    assert g._id == '$field'
    assert g.build() == {'$group':{'_id':'$field'}}

def test_Group_list():
    g = Group().id(['field1','field2','field3'])

    _id = {'field1':'$field1','field2':'$field2','field3':'$field3'}

    assert g._id == _id
    assert g.build() == {'$group':{'_id':_id}}

def test_Group_count():
    g = Group().id('field').count()

    count = {'$sum':1}
    assert g._extra['count'] == count
    assert g.build() == {'$group':{'_id':'$field','count':{'$sum':1}}}

def test_Group_push_one():
    g = Group().id('field').push('name','pushed')

    assert g._extra['name'] == {'$push':'$pushed'}
    assert g.build()['$group']['name'] == {'$push':'$pushed'}

def test_Group_push_many():
    fields = ['field1','field2','field3']
    g = Group().id('id').push('name', fields)

    assert 'name' in g._extra
    assert g._extra['name'] == {'$push': \
        {'field1':'$field1','field2':'$field2','field3':'$field3'}}

def test_group_Group():
    g = Group().id('id')
    q = Query().group(g)

    assert q._pipeline[-1] == g.build()