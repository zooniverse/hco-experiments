################################################################
# Class to construct a query dictionary

class Query:

    def __init__(self):
        self._group = {}
        self._match = {}
        self._limit = 0
        self._project = {}

    def limit(self, num):
        """
            Limits number of results to return
        """
        self._limit = num

        return self

    def match(self, key, value):
        """
            Limits results to documents where the field 'key'
            matches with value
        """
        self._match[key] = value
        return self

    def newField(self, name, value):
        """
            Adds a new field with a static value
        """
        self._project[name] = {'$literal': value}
        return self

    def fields(self, fields):
        """
            Limits the fields that are returned
        """
        if type(fields) is str:
            fields = [fields]

        if type(fields) is list or type(fields) is set:
            for field in fields:
                self._project[field] = 1

        return self

    def group(self, by, count=False):
        """
            Groups the data by the fields in by

            If count=True then adds a field counting
            number of entries in each group
        """
        pipeline = {}
        groupby = {}
        if type(by) is str:
            by = [by]

        if type(by) is list or type(by) is set:
            for field in by:
                groupby[field] = "$%s" % str(field)

        elif type(by) is dict:
            groupby = by

        if groupby:
            pipeline['_id'] = groupby

            if count:
                pipeline['count'] = {'$sum':1}



        self._group = pipeline

        return self

    def build(self):
        """
            Builds an SOM out of this object 
            for the mongo aggregation pipeline
        """
        pipeline = []

        if self._group:
            pipeline.append({'$group': self._group})
        
        if self._match:
            pipeline.append({'$match': self._match})

        if self._project:
            pipeline.append({'$project': self._project})

        if self._limit:
            pipeline.append({'$limit': self._limit})

        return pipeline


