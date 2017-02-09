################################################################
# Class to construct a query dictionary

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
    def __init__(self):
        self._id = False
        self._extra = {}

    def id(self, name):
        if type(name) is str:
            self._id = '$%s' % name
        elif type(name) is list:
            _id = {}
            for field in name:
                _id[field] = '$%s' % field
            self._id = _id

        return self

    def push(self, name, fields):
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
        self._extra[name] = {'$sum':1}

        return self

    def build(self):
        output = {}
        if self._id:
            output['_id'] = self._id
            output.update(self._extra)

            print(output)

            return {'$group': output}
        else:
            raise ValueError('Nothing set for group stage!')



