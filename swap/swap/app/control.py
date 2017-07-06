
import swap.control
import swap.config as config
from swap.utils.classification import Classification
from swap.utils.parsers import ClassificationParser

import sys
import threading
import logging
from queue import Queue

logger = logging.getLogger(__name__)


# def parse_classification(data):
#     logger.debug(data)
#     annotation = parse_annotation(data['annotations'])
#
#     params = {
#         'subject': data['subject_id'],
#         'user': data['user_id'],
#         'annotation': annotation
#     }
#     logger.debug('parsed classification: %s', str(params))
#
#     classification = Classification(**params)
#     logger.debug(classification)
#
#     return classification
#
#
# def parse_annotation(annotations):
#     # TODO parsing annotations for multiple tasks
#     logger.debug('parsing annotations: %s', str(annotations))
#
#     value = list(annotations.values())[0][0]['value']
#
#     logger.debug('got %s', str(value))
#     return value
#

class OnlineControl(swap.control.Control):
    """
    Controller for SWAP in online mode
    """

    def __init__(self):
        super().__init__()
        self.parser = ClassificationParser(config.database.builder)

        if config.database.name == 'swapDB':
            raise Exception('Refusing to use swapDB database in online mode')
            sys.exit(1)
        logger.debug('Initialized online controller')

    def subjects_changed(self):
        # return subjects whose scores have changed
        pass

    def parse_classification(self, args):
        logger.debug('parsing raw classification %s', str(args))
        data = self.parser.process(args)
        cl = Classification.generate(data)
        return cl

    def classify(self, raw_cl):
        # Add classification from caesar
        classification = self.parse_classification(raw_cl)
        logger.debug('Adding classification from network: %s',
                     str(classification))
        self.swap.classify(classification)

        subject = self.swap.subjects.get(classification.subject)
        return subject


class Message:

    def __init__(self, command, data,
                 callback=None, condition=None):
        self.command = command
        self.data = data
        self.callback = callback
        self.condition = condition


class ThreadedControl(threading.Thread):

    def __init__(self, swap=None, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)

        self._queue = Queue()
        self.exit = threading.Event()
        self.daemon = True

        self.control_lock = threading.Lock()
        self.control = OnlineControl()

        if swap is not None:
            self.control.setSWAP(swap)

    def command(self, message):
        if message.command == 'classify':
            self.classify(message)

    def queue(self, command, data, callback=None):
        self._queue.put(Message(command, data, callback))

    def classify(self, message):
        classification = message.data
        if classification is not None:
            with self.control_lock:
                logger.info('classifying')
                subject = self.control.classify(classification)
                logger.info('responding with subject %s score %.4f',
                            subject.id, subject.score)

                message.callback(subject)

    def scores(self):
        with self.control_lock:
            logger.info('generating score export')
            scores = self.control.swap.score_export()
            logger.info('done')

            return scores

    def run(self):
        """
        Main thread for processing classifications
        """
        self.control.run()
        # Ensure thread doesn't exit
        # Wait for classifications in queue
        while not self.exit.is_set():

            message = self._queue.get()
            if message is not None:
                self.command(message)

        logger.warning('thread exiting')

    # def process_message(self, classification):
    #     """
    #     Process a classification and PUT response to caesar
    #     """
    #     with self.control_lock:
    #         logger.info('classifying')
    #         subject = self.control.classify(classification)
    #         logger.info('responding with subject %s score %.4f',
    #                     subject.id, subject.score)

    #         self.respond(subject)


# class OnlineControl(_OnlineControl, metaclass=Singleton):
#     pass
