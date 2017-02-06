#!/usr/bin/env python
################################################################
# Script to load a csv file to the mongo database, 
# as described in the config.yaml

from swap.config import Config
from swap.mongo import DB

import csv
import os
import sys
import argparse

db = DB()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()
    print("Using file %s" % args.file)

    if not os.path.isfile(args.file):
        raise FileNotFoundError("Couldn't find file at '%s'" % args.file)
    if args.file.split('.')[-1] != 'csv':
        raise ValueError("File '%s' not a valid csv file" % args.file)


    file = args.file
    count = 0
    to_upload = []
    total_count = 0

    db.classifications.drop()

    with open(file, 'r') as csvfile:
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