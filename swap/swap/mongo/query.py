################################################################
# Class to construct a query dictionary

from collections import OrderedDict


class Query:

    def __init__(self):
        self._pipeline = []

    def limit(self, num):
        """
            Limits number of results to return
        """
        if not type(num) is int:
            raise ValueError('Limit needs to by type int')
        self._pipeline.append({'$limit': num})

        return self

    def match(self, key, value, eq=True):
        """
            Limits results to documents where the field 'key'
            matches with value
        """
        if eq:
            match = {'$match': {key: value}}
        else:
            match = {'$match': {key: {'$ne': value}}}
        self._pipeline.append(match)
        return self

    def match_range(self, field, lower, upper):
        """
            Limits results to documents where the field 'field'
            is greater equal 'lower' and less than 'upper'
        """
        match_range = {'$match': {field: {'$gte': lower, '$lt': upper}}}

        self._pipeline.append(match_range)
        return self

    def project(self, fields):
        """
            Limits the fields that are returned
        """
        project = {}
        if type(fields) is str:
            fields = [fields]

        if type(fields) is list or type(fields) is set:
            for field in fields:
                if type(field) is tuple:
                    project[field[0]] = {'$literal': field[1]}
                else:
                    project[field] = 1

        elif type(fields) is dict:
            project = fields

        self._pipeline.append({'$project': project})
        return self

    def group(self, by, count=False):
        """
            Groups the data by the fields in by

            If count=True then adds a field counting
            number of entries in each group
        """
        if type(by) is Group:
            g = by
        else:
            g = Group().id(by)
            if count:
                g.count()

        self._pipeline.append(g.build())
        return self

    def sort(self, s):
        """
            Sorts the data via a Sort object
        """
        if not type(s) is Sort:
            raise ValueError("sort must receive a Sort class object")

        self._pipeline.append(s.build())
        return self

    def out(self, collection):
        """
            Writes query results to the specified collection
        """
        if not type(collection) is str:
            raise ValueError("Collection name needs to be string")

        self._pipeline.append({'$out': collection})
        return self


    def build(self):
        """
            Builds an SOM out of this object
            for the mongo aggregation pipeline
        """
        return self._pipeline

class Group:
    """
        Buils a $group statement in the aggregation pipeline.
        $group is more complicated than the other commands,
        so it deserves its own class
    """
    def __init__(self):
        self._id = False
        self._extra = {}


    def id(self, name):
        """
            Defines the _id field that the documents are
            grouped by
        """
        if type(name) is str:
            self._id = '$%s' % name
        elif type(name) is list:
            _id = {}
            for field in name:
                _id[field] = '$%s' % field
            self._id = _id

        return self

    def push(self, name, fields):
        """
            Args:
                name (str) name of the pushed array
                fields (list) list of fields to push

            After grouping, pushes an array containing the
            specified fields from the documents aggregated into
            this group.
        """
        if type(fields) is str:
            push = '$%s' % fields

        if type(fields) is list:
            push = {}
            for field in fields:
                push[field] = '$%s' % field

        elif type(fields) is dict:
            push = fields

        self._extra[name] = {'$push':push}

        return self

    def count(self, name='count'):
        """
            Add an extra field counting the number of documents
            in each group
        """
        self._extra[name] = {'$sum':1}

        return self

    def build(self):
        """
            Build a dict out of this object for the mongo
            aggregation pipeline
        """
        output = {}
        if self._id:
            output['_id'] = self._id
            output.update(self._extra)

            print(output)

            return {'$group': output}
        else:
            raise ValueError('Nothing set for group stage!')

        return self

class Sort:

    def __init__(self):
        self._order = OrderedDict()

    def add(self, name, order):
        """
            Args:
                name (str) field name
                order (int) 1 ascending, -1 descending
            Sorts the aggregation results by the field name
            in asc/desc order
        """
        self._order[name] = order
        return self

    def addMany(self, order):
        """
            Args:
                order list(tuple(name, order))

            Receives multiple sort commands as list of tuples,
            where each tuple has the field name and asc/desc order
        """
        for name, direction in order:
            self._order[name] = direction
        return self

    def build(self):
        return {'$sort':self._order}