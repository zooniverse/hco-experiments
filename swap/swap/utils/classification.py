
from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)


class Classification:
    """
        Object to represent each individual classification
    """

    def __init__(self, user, subject, annotation):
        """
            Parameters
            ----------
            user : str
                user name of the classifying user
            subject : int
                id number of the subject being classified
            annotation : int
                label assigned by the user
            gold_label : int
                (optional) expert assigned label
            metadata : dict
                (optional) any additional metadata associated
        """

        if type(annotation) is not int:
            raise ClValueError('annotation', int, annotation)

        self.user = user
        self.subject = subject
        self.annotation = annotation

    def __str__(self):
        return 'user %s subject %s annotation %d' % \
            (str(self.user), str(self.subject),
             self.annotation)

    @staticmethod
    def generate(cl):
        """
            Static generator method. Generates a classification
            object from a classification in dictionary form
        """
        Classification.Validate(cl)

        user = cl['user_id']
        if user is None:
            user = cl['session_id']

        subject = cl['subject_id']
        annotation = cl['annotation']

        c = Classification(user, subject, annotation)
        logger.debug(c)

        return c

    @staticmethod
    def Validate(cl):
        """
            Verify classification is compatible with current
            SWAP version

            Parameters
            ----------
            cl : dict
                classification
        """
        names = [
            'user_id',
            'session_id',
            'subject_id',
            'annotation']
        for key in names:
            try:
                cl[key]
            except KeyError:
                raise ClKeyError(key, cl)

        if type(cl['annotation']) is not int:
            raise ClValueError('annotation', int, cl)
        if 'gold_label' in cl and type(cl['gold_label']) is not int:
            raise ClValueError('gold_label', int, cl)


class ClKeyError(KeyError):
    """
    Raise when a classification is missing a key element
    """

    def __init__(self, key, cl={}, *args, **kwargs):
        logger.error(cl)
        msg = 'key %s not found in classification %s' % (key, str(cl))
        KeyError.__init__(self, msg)


class ClValueError(ValueError):
    """
    Raise when a value in the classification is incorrect,
    impossible, or is of the wrong type
    """

    def __init__(self, key, _type, value, *args, **kwargs):
        if type(value) is dict:
            kwargs['cl'] = value
            value = value[key]
        if 'cl' in kwargs:
            logger.error(kwargs['cl'])
        bad_type = type(value)
        msg = 'key %s should be type %s but is %s' % (key, _type, bad_type)
        ValueError.__init__(self, msg)


class PanoptesParser:

    def __init__(self, builder_config):
        types = builder_config._core_types
        # types.update(builder_config.types)

        self.types = types
        self.annotation = builder_config.annotation
        self.timestamp_formats = builder_config._timestamp_format

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
            value = self._type(cl[key], type_)

            # if key == 'retired' and value is None:
            #     value = False

            cl[key] = value

        return cl

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


if __name__ == '__main__':
    import csv
    from pprint import pprint
    import swap.config as config

    pp = PanoptesParser(config.database.builder)
    with open('/home/michael/Downloads/supernova-hunters-classifications-100.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            print(pp.process(row))
