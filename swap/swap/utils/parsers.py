
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self, builder_config):
        self.config = builder_config
        self.timestamp_formats = builder_config._timestamp_format
        self.types = self._config_types(builder_config)

    def _config_types(self, config):
        pass

    def _type(self, value, type_):
        # Parse timestamps
        if type_ == "timestamp":
            for fmt in self.timestamp_formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError('timestamp %s format not recognized' % value)

        if value in ['None', 'null', '', None]:
            return None

        if type(value) is not type_:
            if type_ is bool:
                print(value)
                return value in ['True', 'true']

            # Cast value to the expected type
            return type_(value)

        return value

    def _mod_types(self, cl):
        # Convert types specified in config
        # anything not in config is interpreted as str

        # def mod(key, value):
        #     cl[key] = value

        for key, type_ in self.types.items():

            if type(type_) is tuple:
                type_, rename = type_
                cl[key] = cl.pop(rename)

            value = self._type(cl[key], type_)

            # if key == 'retired' and value is None:
            #     value = False

            cl[key] = value

        return cl


class ClassificationParser(Parser):

    def __init__(self, builder_config):
        super().__init__(builder_config)
        self.annotation = builder_config.annotation

    def _config_types(self, config):
        return config._core_types

    def parse_annotations(self, cl):
        annotations = json.loads(cl['annotations'])

        for data in annotations:
            if data['task'] == self.annotation.task:
                value = data['value']

                if value in self.annotation.true:
                    return 1
                if value in self.annotation.false:
                    return 0
                return -1

    def process(self, cl):
        metadata = json.loads(cl['metadata'])

        output = {
            'classification_id': cl['classification_id'],
            'subject_id': cl['subject_ids'],
            'user_name': cl['user_name'],
            'user_id': cl['user_id'],
            'workflow': cl['workflow_id'],
            'time_stamp': cl['created_at'],
        }

        output.update({
            'session_id': metadata['session'],
            'live_project': metadata['live_project'],
            'seen_before': metadata.get('seen_before', False)
        })

        output['annotation'] = self.parse_annotations(cl)

        output = self._mod_types(output)
        return output


class MetadataParser(Parser):

    def __init__(self, builder_config):
        super().__init__(builder_config)

        self.metadata = builder_config.subject_metadata

    def _config_types(self, config):
        return config.subject_metadata

    def process(self, cl):
        output = self._mod_types(cl)
        return output


if __name__ == '__main__':
    import csv
    from pprint import pprint
    import swap.config as _config

    pp = MetadataParser(_config.database.builder)
    with open('/home/michael/Downloads/SNHunters_classification_dump_20170622_gold-head.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            print(pp.process(row))
