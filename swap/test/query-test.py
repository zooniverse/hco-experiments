################################################################
# Test functions for query class

from swap.mongo.query import Query

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
    q.fields('name')

    assert 'name' in q._project
    assert q._project['name'] == 1

def test_add_fields():
    q = Query()
    q.fields(['field1', 'field2', 'field3'])

    assert len(q._project) == 3
    assert q._project['field1'] == 1
    assert q._project['field2'] == 1
    assert q._project['field3'] == 1

def test_add_fields_set():
    q = Query()
    q.fields({'field1', 'field2', 'field3'})

    assert len(q._project) == 3
    assert q._project['field1'] == 1
    assert q._project['field2'] == 1
    assert q._project['field3'] == 1

def test_project_build():
    q = Query()
    q.fields(['field1', 'field2', 'field3'])
    build = q.build()[0]

    assert '$project' in build
    assert 'field1' in build['$project']
    assert build['$project']['field1'] == 1

    assert 'field2' in build['$project']
    assert build['$project']['field2'] == 1

    assert 'field3' in build['$project']
    assert build['$project']['field3'] == 1
