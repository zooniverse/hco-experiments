#!/usr/bin/env python
################################################################
# Script to build a collection containing subject data 
# from the classifications collection

from swap.config import Config
from swap.mongo import DB
from swap.mongo import Query

from pprint import pprint

def main():
    db = DB()

    fields = ['subject_id','gold_label','diff']
    project = {'_id': '$_id.subject_id', \
               'gold_label': '$_id.gold_label', \
               'diff':'$_id.diff'}

    q = Query()
    q.group(fields).project(project).out('subjects')
    
    print(q.build())

    db.classifications.aggregate(q.build())


if __name__ == '__main__':
    main()