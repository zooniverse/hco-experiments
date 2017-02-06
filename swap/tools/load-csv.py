#!/usr/bin/env python
################################################################
# Script to load a csv file to the mongo database, 
# as described in the config.yaml

from swap.config import Config
from swap.mongo import DB

import csv
import os
import sys

db = DB()


def main():
    path = os.path.dirname(os.path.realpath(__file__))
    folder = '.'
    fname = 'SNHunters_classification_dump_20170109_metadata.csv'

    count = 0
    to_upload = []
    total_count = 0

    db.classifications.drop()

    with open('/'.join((path, folder, fname)), 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')

        for row in reader:
            to_upload.append(processRow(row))

            #print("%d: %s" % (total_count, str(row)))
            sys.stdout.write("%d records processed\r" % total_count)
            sys.stdout.flush()
            
            total_count += 1
            count += 1
            if count >= 100000:
                upload(to_upload)
                to_upload = []

                count = 0

def processRow(row):
    return row

def upload(rows):
    db.classifications.addMany(rows)



    

if __name__ == "__main__":
    main()