
from swap.db.db import Collection
import swap.utils.parsers as parsers
import swap.config as config

import sys
import csv
import logging
logger = logging.getLogger(__name__)


class Subjects(Collection):

    @staticmethod
    def _collection_name():
        return 'subjects'

    @staticmethod
    def _schema():
        return config.parser.subject_metadata

    def _init_collection(self):
        pass

    #######################################################################

    def get_metadata(self, subject_id):
        cursor = self.collection.find({'subject': subject_id}).sort('_id', -1)

        try:
            data = cursor.next()
            data.pop('_id')
            return data
        except StopIteration:
            pass

    def upload_metadata_dump(self, fname):
        self._rebuild()

        logger.info('parsing csv dump')
        data = []
        parser = parsers.MetadataParser('csv')

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
                    self.collection.insert_many(data)
                    data = []

        self.collection.insert_many(data)
        logger.debug('done')
