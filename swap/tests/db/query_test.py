################################################################
# Test functions for query class

from swap.db.query import Query
from swap.db.query import Group
from swap.db.query import Sort

from collections import OrderedDict


class Test_Query:
    ################################################################
    # Limit
    def test_limit(self):
        q = Query()
        q.limit(5)
        assert q._pipeline[-1] == {'$limit': 5}

    ################################################################
    # Match
    def test_match_eq(self):
        q = Query()
        q.match('key', 'value')
        assert q._pipeline[-1] == {'$match': {'key': 'value'}}

    def test_match_neq(self):
        q = Query()
        q.match('key', 'value', False)

        assert q._pipeline[-1] == {'$match': {'key': {'$ne': 'value'}}}

    ################################################################
    # Match Range
    def test_match_range(self):
        q = Query()
        q.match_range('field', lower=15, upper=20)

        assert q._pipeline[-1] == \
            {'$match': {'field': {'$gte': 15, '$lt': 20}}}

    ################################################################
    # Project
    def test_add_new_field(self):
        q = Query()
        q.project([('name', 100)])

        assert q._pipeline[-1] == {'$project': {'name': {'$literal': 100}}}

    def test_project_str(self):
        q = Query()
        q.project('name')

        assert q._pipeline[-1] == {'$project': {'name': 1}}

    def test_add_fields_list(self):
        q = Query()
        fields = ['field1', 'field2', 'field3']
        q.project(fields)

        assert q._pipeline[-1] == {
            '$project': {'field1': 1,
                         'field2': 1,
                         'field3': 1}}

    def test_add_fields_set(self):
        q = Query()
        fields = {'field1', 'field2', 'field3'}
        q.project(fields)

        assert q._pipeline[-1] == {
            '$project': {'field1': 1,
                         'field2': 1, 'field3': 1}}

    def test_add_fields_dict(self):
        q = Query()
        fields = {'field1': '$field1', 'field2': '$field2'}
        q.project(fields)

        assert q._pipeline[-1] == {'$project': fields}

    ################################################################
    # Out

    def test_out(self):
        q = Query()
        q.out('collection')

        assert q._pipeline[-1] == {'$out': 'collection'}

    ################################################################
    # Group
    def test_group_str(self):
        q = Query()
        q.group("field")

        assert q._pipeline[-1] == {'$group': {"_id": "$field"}}

    def test_group_list(self):
        q = Query()
        q.group(['field1', 'field2'])

        assert q._pipeline[-1] == {'$group': {'_id': {
                                   'field1': '$field1',
                                   'field2': '$field2'}}}

    def test_group_count(self):
        q = Query()
        q.group('field', count=True)

        assert q._pipeline[-1] == {
            '$group': {'_id': '$field',
                       'count': {'$sum': 1}}}


class Test_Group:
    # ###############################################################
    # Group Class

    def test_Group_str(self):
        g = Group().id('field')

        assert g._id == '$field'
        assert g.build() == {'$group': {'_id': '$field'}}

    def test_Group_list(self):
        g = Group().id(['field1', 'field2', 'field3'])

        _id = {'field1': '$field1', 'field2': '$field2', 'field3': '$field3'}

        assert g._id == _id
        assert g.build() == {'$group': {'_id': _id}}

    def test_Group_count(self):
        g = Group().id('field').count()

        count = {'$sum': 1}
        assert g._extra['count'] == count
        assert g.build() == {'$group': {'_id': '$field', 'count': {'$sum': 1}}}

    def test_Group_push_one(self):
        g = Group().id('field').push('name', 'pushed')

        assert g._extra['name'] == {'$push': '$pushed'}
        assert g.build()['$group']['name'] == {'$push': '$pushed'}

    def test_Group_push_many(self):
        fields = ['field1', 'field2', 'field3']
        g = Group().id('id').push('name', fields)

        assert 'name' in g._extra
        assert g._extra['name'] == {
            '$push': {'field1': '$field1',
                      'field2': '$field2', 'field3': '$field3'}}

    def test_group_Group(self):
        g = Group().id('id')
        q = Query().group(g)

        assert q._pipeline[-1] == g.build()


class Test_Sort:
    ################################################################
    # Sort Class

    def test_Sort_one(self):
        s = Sort()
        s.add('field', 1)

        assert s._order['field'] == 1

    def test_Sort_two_order(self):
        s = Sort()
        s.add('field1', 1).add('field2', -1)

        order = list(s._order)
        assert order[0] == 'field1'
        assert order[1] == 'field2'

    def test_Sort_two_values(self):
        s = Sort()
        s.add('field1', 1).add('field2', -1)

        assert s._order['field1'] == 1
        assert s._order['field2'] == -1

    def test_Sort_many_order(self):
        s = Sort()
        s.addMany([('field1', 1), ('field2', -1)])

        order = list(s._order)
        assert order[0] == 'field1'
        assert order[1] == 'field2'

    def test_Sort_many_values(self):
        s = Sort()
        s.addMany([('field1', 1), ('field2', -1)])

        assert s._order['field1'] == 1
        assert s._order['field2'] == -1

    def test_Sort_build(self):
        fields = [('field1', 1), ('field2', -1)]
        s = Sort()
        s.addMany(fields)

        b = s.build()
        assert b['$sort'] == OrderedDict(fields)
