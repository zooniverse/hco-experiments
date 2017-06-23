
import swap.control
from swap.utils.classification import Classification

import logging

logger = logging.getLogger(__name__)


def parse_classification(data):
    logger.debug(data)
    annotation = parse_annotation(data['annotations'])

    params = {
        'subject': data['subject_id'],
        'user': data['user_id'],
        'annotation': annotation
    }
    logger.debug('parsed classification: %s', str(params))

    classification = Classification(**params)
    logger.debug(classification)

    return classification


def parse_annotation(annotations):
    # TODO parsing annotations for multiple tasks
    logger.debug('parsing annotations: %s', str(annotations))

    value = list(annotations.values())[0][0]['value']

    logger.debug('got %s', str(value))
    return value


class OnlineControl(swap.control.Control):
    """
    Controller for SWAP in online mode
    """

    def __init__(self):
        super().__init__()
        self.run()
        logger.debug('Initialized online controller')

    def subjects_changed(self):
        # return subjects whose scores have changed
        pass

    @staticmethod
    def parse_classification(args):
        return parse_classification(args)

    def classify(self, classification):
        # Add classification from caesar
        logger.debug('Adding classification from network: %s',
                     str(classification))
        self.swap.classify(classification)

        subject = self.swap.subjects.get(classification.subject)
        return subject


# class OnlineControl(_OnlineControl, metaclass=Singleton):
#     pass
