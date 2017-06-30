#!/usr/bin/env python
################################################################
# Script to load a csv file to the mongo database,
# as described in the config.yaml

import swap.db
import swap.config as config

import csv
import os
import sys
import argparse
from datetime import datetime

meta_names = config.database.builder.metadata
core_names = config.database.builder.core

types = config.database.builder._core_types
types.update(config.database.builder.types)


def main():
    db = swap.db.DB()

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
    db._init_classifications()

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

    db._gen_stats()


def processRow(row):
    # Convert types specified in config
    # anything not in config is interpreted as str

    def mod(key, value):
        row[key] = value

    for key, type_ in types.items():
        value = row[key]

        # Parse timestamps
        if type_ == "timestamp":
            mod(key, datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ"))

        # Replace cells that should be a number with 0
        # Except user_id, which gets -1 if empty
        elif value == '' and type_ in [int, float]:
            if key == 'user_id':
                mod(key, -1)
            else:
                mod(key, 0)

        elif value == 'None':
            mod(key, -1)

        elif type_ is bool:
            mod(key, value == 'True')

        # Cast value to the expected type
        elif type(value) is not type_:
            mod(key, type_(value))

    def pull(keys):
        output = {}
        for key in keys:
            output[key] = row[key]

        return output

    metadata = pull(meta_names)
    core = pull(core_names)

    core['metadata'] = metadata

    # print(row)
    return core


def upload(rows):
    db = swap.db.DB()
    db.classifications.insert_many(rows)


if __name__ == "__main__":
    main()
