
from swap.db import DB
import swap.utils.parsers as parsers
import swap.config as config

import sys
import csv
import logging
logger = logging.getLogger(__name__)

subject_count = None
collection = DB().subjects


def aggregate(*args, **kwargs):
    try:
        logger.debug('Preparing to run aggregation')
        logger.debug(*args, **kwargs)
        return collection.aggregate(*args, **kwargs)
    except Exception as e:
        logger.error(e)
        raise e


def upload_metadata_dump(fname):
    logger.info('dropping collection')
    DB()._db.subjects.drop()

    logger.info('parsing csv dump')
    data = []
    parser = parsers.MetadataParser(config.database.builder)

    with open(fname, 'r') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader):
            item = parser.process(row)
            print(item)
            data.append(item)

            sys.stdout.flush()
            sys.stdout.write("%d records processed\r" % i)

            if len(data) > 100000:
                print(data)
                collection.insert_many(data)
                data = []

    collection.insert_many(data)
    logger.debug('done')
