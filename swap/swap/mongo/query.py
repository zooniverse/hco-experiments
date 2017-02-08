################################################################
# Class to construct a query dictionary

class Query:

    def __init__(self):
        self._match = {}
        self._limit = 0
        self._project = {}

    def limit(self, num):
        self._limit = num

        return self

    def match(self, key, value):
        self._match[key] = value
        return self

    def newField(self, name, value):
        self._project[name] = {'$literal': value}
        return self

    def fields(self, fields):
        if type(fields) is str:
            fields = [fields]

        if type(fields) is list or type(fields) is set:
            for field in fields:
                self._project[field] = 1

        return self

    def build(self):
        pipeline = []

        
        if len(self._match) > 0:
            pipeline.append({'$match': self._match})

        if len(self._project) > 0:
            pipeline.append({'$project': self._project})

        if self._limit > 0:
            pipeline.append({'$limit': self._limit})

        return pipeline


