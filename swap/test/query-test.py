################################################################
# Test functions for query class

from swap.mongo.query import Query

################################################################
# Limit
def test_limit():
    q = Query()
    q.limit(5)
    assert q._limit == 5

def test_limit_not_build():
    q = Query()
    q.limit(0)
    build = q.build()

    for item in build:
        assert '$limit' not in item

def test_limit_build():
    q = Query()
    q.limit(5)
    build = q.build()[0]
    assert '$limit' in build
    assert build['$limit'] == 5

################################################################
# Match
def test_match():
    q = Query()
    q.match('key', 'value')
    assert 'key' in q._match
    assert q._match['key'] == 'value'

def test_match_build():
    q = Query()
    q.match('key', 'value')
    build = q.build()[0]

    assert '$match' in build
    assert 'key' in build['$match']
    assert build['$match']['key'] == 'value'

################################################################
# Project
def test_add_new_field():
    q = Query()
    q.newField('name', 100)

    assert 'name' in q._project
    assert '$literal' in q._project['name']
    assert q._project['name']['$literal'] == 100

def test_add_new_field_build():
    q = Query()
    q.newField('name', 100)

    build = q.build()[0]
    assert build['$project'] == {'name': {'$literal': 100}}

def test_add_field():
    q = Query()
    q.project('name')

    assert 'name' in q._project
    assert q._project['name'] == 1

def test_add_fields():
    q = Query()
    q.project(['field1', 'field2', 'field3'])

    assert len(q._project) == 3
    assert q._project['field1'] == 1
    assert q._project['field2'] == 1
    assert q._project['field3'] == 1

def test_add_fields_set():
    q = Query()
    q.project({'field1', 'field2', 'field3'})

    assert len(q._project) == 3
    assert q._project['field1'] == 1
    assert q._project['field2'] == 1
    assert q._project['field3'] == 1

def test_add_fields_dict():
    q = Query()
    fields = {'field1':'$field1', 'field2':'$field2'}
    q.project(fields)

    assert q._project == fields


def test_project_build():
    q = Query()
    q.project(['field1', 'field2', 'field3'])
    build = q.build()[0]

    assert '$project' in build
    assert 'field1' in build['$project']
    assert build['$project']['field1'] == 1

    assert 'field2' in build['$project']
    assert build['$project']['field2'] == 1

    assert 'field3' in build['$project']
    assert build['$project']['field3'] == 1

################################################################
# Group

def test_group_str():
    q = Query()
    q.group("field")

    assert q._group == {"_id":{"field":"$field"}}

def test_group_list():
    q = Query()
    q.group(['field1','field2'])

    assert q._group == {"_id":{'field1':'$field1','field2':'$field2'}}

def test_group_set():
    q = Query()
    q.group({'field1','field2'})

    assert q._group == {"_id":{'field1':'$field1','field2':'$field2'}}

def test_group_list():
    q = Query()
    q.group(['field1','field2'])

    assert q._group == {"_id":{'field1':'$field1','field2':'$field2'}}

def test_group_count():
    q = Query()
    q.group('field',count=True)

    assert q._group == {'_id':{'field':'$field'},'count':{'$sum':1}}

def test_group_build():
    q = Query()
    q.group('field')

    assert '$group' in q.build()[0]

def test_group_not_build():
    q = Query()
    q.limit(5)

    for i in q.build():
        assert '$group' not in i

################################################################
# Out

def test_out():
    q = Query()
    q.out('collection')

    assert q._out == 'collection'

def test_out_build():
    q = Query()
    q.limit(5).out('collection')

    assert q.build()[-1] == {'$out':'collection'}