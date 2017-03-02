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
config = Config()
_meta_names = config.database['metadata']


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

            # print("%d: %s" % (total_count, str(row)))
            sys.stdout.flush()
            sys.stdout.write("%d records processed\r" % total_count)

            total_count += 1
            count += 1
            if count >= 100000:
                upload(to_upload)
                to_upload = []

                count = 0

    upload(to_upload)


def processRow(row):
    # Convert types specified in config
    # anything not in config is interpreted as str
    for key, t in config.csv_types.items():
        value = row[key]
        # print(key, t, value)

        if value == '' and t in ['int', 'float']:
            if key == 'user_id':
                value = -1
            else:
                value = 0

        if t == 'int':
            row[key] = int(value)
        elif t == 'float':
            row[key] = float(value)

    metadata = {}
    for m in _meta_names:
        metadata[m] = row[m]
        del row[m]

    row['metadata'] = metadata

    # print(row)
    return row


def upload(rows):
    db.classifications.insert_many(rows)


if __name__ == "__main__":
    main()
