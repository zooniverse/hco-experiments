
import logging
logger = logging.getLogger(__name__)


class Classification:
    """
        Object to represent each individual classification
    """

    def __init__(self, user, subject, annotation,
                 gold_label=-1, metadata={}):
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

        if type(gold_label) is not int:
            raise ClValueError('gold_label', int, gold_label)

        if type(metadata) is not dict:
            raise ClValueError('metadata', dict, metadata)

        self.user = user
        self.subject = subject
        self.annotation = annotation

        self.gold_label = None
        self.gold = gold_label

        self.metadata = metadata

    @property
    def gold(self):
        """
            Get the gold label
        """
        if self.gold_label is not None:
            return self.gold_label
        else:
            return False

    @gold.setter
    def gold(self, gold):
        if gold in [0, 1]:
            self.gold_label = gold
        else:
            self.gold_label = None

    def isgold(self):
        """
        If the classification has a gold label associated with it
        """
        if self.gold_label is not None:
            return True
        else:
            return False

    def __str__(self):
        return 'user %s subject %s annotation %d gold %s' % \
            (str(self.user), str(self.subject),
             self.annotation, str(self.gold))

    @staticmethod
    def generate(cl):
        """
            Static generator method. Generates a classification
            object from a classification in dictionary form
        """
        Classification.Validate(cl)

        user = cl['user_id']
        if user == -1:
            user = cl['session_id']

        subject = cl['subject_id']
        annotation = cl['annotation']

        c = Classification(user, subject, annotation)

        if 'gold_label' in cl:
            c.gold_label = cl['gold_label']

        if 'metadata' in cl:
            c.metadata = cl['metadata']

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
