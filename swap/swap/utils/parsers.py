
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

    def _remap(self, cl):
        for key, remap in self.types.items():
            if type(remap) is tuple:
                remap = remap[1]
                if type(remap) is not tuple:
                    remap = (remap)

                for old_key in remap:
                    if old_key in cl:
                        cl[key] = cl.pop(old_key)
                        break

        return cl

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
                type_ = type_[0]

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

    def _find_value(self, root_value):
        steps = self.annotation.value_key.split('.')
        item = root_value

        logger.debug('navigating %s in %s', str(steps), str(item))

        for key in steps:
            if type(item) is list:
                key = int(key)

            item = item[key]

        return item

    def _parse_value(self, value):
        if self.annotation.value_key is not None:
            value = self._find_value(value)

        if value in self.annotation.true:
            return 1
        if value in self.annotation.false:
            return 0

    def _find_task(self, annotations):
        task = self.annotation.task
        if type(annotations) is dict and task in annotations:
            return annotations[task][0]

        if type(annotations) is list:
            for annotation in annotations:
                if annotation['task'] == self.annotation.task:
                    return annotation

    def parse_annotations(self, cl):
        annotations = self.parse_json(cl['annotations'])
        logger.debug('parsing annotation %s', annotations)

        annotation = self._find_task(annotations)

        value =  self._parse_value(annotation['value'])
        if value is None:
            logger.critical('Coult not find valid annotation for classification')
            logger.debug(cl)

        return value

    def parse_subject(self, cl):
        for key in ['subject_id', 'subject_ids']:
            if key in cl:
                return cl[key]
        raise KeyError('Can\'t find subject in classification' % cl)

    @staticmethod
    def parse_json(item):
        if type(item) is str:
            return json.loads(item)
        return item

    def process(self, cl):
        cl = self._remap(cl)
        metadata = self.parse_json(cl['metadata'])

        output = {
            'classification_id': cl['classification_id'],
            'user_id': cl['user_id'],
            'workflow': cl['workflow_id'],
            'time_stamp': cl['created_at'],
        }

        output.update({
            'session_id': metadata['session'],
            'live_project': metadata['live_project'],
            'seen_before': metadata.get('seen_before', False)
        })

        output['subject_id'] = self.parse_subject(cl)
        output['annotation'] = self.parse_annotations(cl)

        output = self._mod_types(output)

        if output['annotation'] is None:
            return None
        return output


class MetadataParser(Parser):

    def __init__(self, builder_config):
        super().__init__(builder_config)

        self.metadata = builder_config.subject_metadata

    def _config_types(self, config):
        return config.subject_metadata

    def process(self, cl):
        cl = self._remap(cl)
        output = self._mod_types(cl)
        return output


if __name__ == '__main__':
    import csv
    from pprint import pprint
    import swap.config as _config

    # pp = MetadataParser(_config.database.builder)
    # with open('/home/michael/Downloads/SNHunters_classification_dump_20170622_gold-head.csv') as file:
    #     reader = csv.DictReader(file)
    #     for row in reader:
    #         print(row)
    #         print(pp.process(row))

    pp = ClassificationParser(_config.database.builder)
    with open('/home/michael/Downloads/supernova-hunters-classifications-100.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            print(pp.process(row))
