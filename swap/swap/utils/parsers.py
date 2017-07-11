
import swap.config

from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class Parser:

    def __init__(self, source):
        self.timestamp_formats = swap.config.parser._timestamp_format
        self.source = source

    @property
    def config(self):
        """
        Return the type mapping in the config used for this parser
        """
        pass

    @staticmethod
    def _navigate(obj, dotkey, split='.'):
        steps = dotkey.split(split)
        item = obj

        logger.debug('navigating to %s', str(steps))

        for key in steps:
            if type(item) is list:
                key = int(key)

            item = item[key]

        return item

    def _remap(self, cl, key, field):
        """
        Remap keys in the classification dump as specified in config

        if there is a type entry in the config like:
            'name': (int, 'other_name')
        this will look for 'other_name' in a raw classification in the cl blob
        and modify its key to 'name'
        """
        if 'remap' in field:
            remap = field['remap']

            if type(remap) is dict:
                if self.source in remap:
                    remap = remap[self.source]

                    if type(remap) is not list:
                        remap = [remap]
            elif type(remap) is str:
                remap = [remap]
            elif type(remap) is not list:
                raise self.MissingInformation(field, 'remap')

            for old_key in remap:
                try:
                    return self._navigate(cl, old_key)
                except KeyError:
                    pass
        if key in cl:
            return cl[key]

        if 'ifgone' in field:
            return field['ifgone']

        raise self.MissingInformation(cl, key)

    def _type(self, value, type_):
        """
        Casts a value in the classification stream as specified in config

        if there is a type entry in the config like:
            'name': int
        this will receive the value of 'name' in the classification and
        cast it as an int. Other supported types are float, bool, timestamp,
        and str.
        """
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
                if value in ['True', 'true']:
                    return True
                if value in ['False', 'false']:
                    return False
                raise TypeError('Can\'t parse %s as bool' % value)

            # Cast value to the expected type
            return type_(value)

        return value

    def _mod_fields(self, cl):
        """
        Casts values in the classification stream as specified in config

        if there is a type entry in the config like:
            'name': int
        this will look for 'name' in the classification and
        cast it as an int.
        """
        # Convert types specified in config
        # anything not in config is interpreted as str

        # def mod(key, value):
        #     cl[key] = value

        out = {}
        for key, field in self.config.items():
            type_ = field.get('type', str)
            value = self._remap(cl, key, field)
            value = self._type(value, type_)

            out[key] = value

        return out

    @staticmethod
    def parse_json(item):
        if type(item) is str:
            try:
                return json.loads(item)
            except json.decoder.JSONDecodeError:
                logger.error('Couldn\'t parse json from %s', item)
        return item

    def process(self, cl):
        return self._mod_fields(cl)

    class MissingInformation(Exception):
        def __init__(self, cl, key):
            msg = 'Couldn\'t parse \'%s\' out of classification %s' % \
                (key, str(cl))
            super().__init__(msg)


class ClassificationParser(Parser):

    def __init__(self, source):
        super().__init__(source)
        self.annotation = AnnotationParser(source)

    @property
    def config(self):
        return swap.config.parser.classification

    def parse_subject(self, cl):
        for key in ['subject_id', 'subject_ids']:
            if key in cl:
                return cl[key]
        raise self.MissingInformation(cl, 'subject')

    def process(self, cl):
        cl['metadata'] = self.parse_json(cl['metadata'])
        cl['annotation'] = self.annotation.process(cl)
        out = super().process(cl)

        return out


class AnnotationParser(Parser):

    @property
    def config(self):
        return swap.config.parser.annotation

    def process(self, cl):
        annotations = self.parse_json(cl['annotations'])
        logger.debug('parsing annotation %s', annotations)

        annotation = self._find_task(annotations)

        value = self._parse_value(annotation['value'])
        if value is None:
            logger.error('Coult not find valid annotation for classification')
            task = self.config.task
            value_key = self.config.value_key
            raise self.MissingAnnotation(cl, task, value_key)

        return value

    def _find_task(self, annotations):
        """
        Find the right task from the annotation field in a classification

        Needs to be dynamic because csv dump and caesar stream send
        classifications with different formats
        """
        task = self.config.task
        if type(annotations) is dict and task in annotations:
            return annotations[task][0]

        if type(annotations) is list:
            for annotation in annotations:
                if annotation['task'] == self.config.task:
                    return annotation

    def _parse_value(self, value):
        """
        Parses the value field of an annotation task
        """
        key = self.config.value_key
        sep = self.config.value_separator
        logger.debug('value %s key %s', str(value), key)

        if key is not None:
            value = self._navigate(value, key, sep)

        if value in self.config.true:
            return 1
        if value in self.config.false:
            return 0

    class MissingAnnotation(Parser.MissingInformation):
        def __init__(self, field, task, value_key):
            super().__init__(field, '%s %s' % (task, value_key))


class MetadataParser(Parser):
    """
    Parse subject metadata from csv dump

    NOTE: Not fully tested yet
    """

    @property
    def config(self):
        return swap.config.parser.subject_metadata


class GoldsParser(MetadataParser):
    """
    Parse subject gold standard data from a custom lightweight csv dump

    NOTE: Not fully tested yet
    """

    @property
    def config(self):
        data = swap.config.parser.subject_metadata
        return {k: v for k, v in data.items() if k in ['subject', 'gold']}
