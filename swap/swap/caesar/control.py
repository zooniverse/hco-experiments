
import swap.control
import swap.config as config
from swap.utils.classification import Classification
from swap.utils.parsers import ClassificationParser
from swap.db import DB

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
        self.parser = ClassificationParser('json')

        if config.database.name == 'swapDB':
            raise Exception('Refusing to use swapDB database in online mode')
            sys.exit(1)
        logger.debug('Initialized online controller')

    def subjects_changed(self):
        # return subjects whose scores have changed
        pass

    def get_classifications(self):
        logger.info('Loading dual cursors of dump and caesar classifications')

        cursor1 = DB().classifications.getClassifications()
        cursor2 = DB().caesar.getClassifications()

        return DualCursor(cursor1, cursor2)

    def parse_raw(self, raw_cl):
        logger.debug('parsing raw classification')
        data = self.parser.process(raw_cl)
        return data

    @staticmethod
    def gen_cl(data):
        return Classification.generate(data)

    @staticmethod
    def cl_exists(cl):
        def id_(cl):
            return cl['classification_id']

        return DB().caesar.exists(id_(cl)) or \
            DB().classifications.exists(id_(cl))


    def classify(self, raw_cl):
        # Add classification from caesar
        data = self.parse_raw(raw_cl)
        cl = self.gen_cl(data)

        logger.debug('Checking if already received classification')
        if not self.cl_exists(data):

            logger.debug('Uploading classification to caesar db: %s',
                         str(data))
            DB().caesar.insert(data)

            logger.debug('Adding classification from network: %s',
                         str(cl))
            self.swap.classify(cl)

            subject = self.swap.subjects.get(cl.subject)
            return subject

    def run(self, amount=None):
        def _amt(stats):
            return stats['first_classifications']

        if amount is None:
            amount = _amt(DB().classifications.get_stats())
            amount += _amt(DB().caesar._gen_stats(upload=False))

        super().run(amount=amount)


class Message:

    def __init__(self, command, data,
                 callback=None, condition=None):
        self.command = command
        self.data = data
        self.callback = callback
        self.condition = condition


class ThreadedControl(threading.Thread):

    def __init__(self, swap_=None, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)

        self._queue = Queue()
        self.exit = threading.Event()
        self.daemon = True

        self.control_lock = threading.Lock()
        self.control = OnlineControl()

        if swap_ is not None:
            self.control.setSWAP(swap_)
        else:
            self.control.run()

    def command(self, message):
        if message.command == 'classify':
            self.classify(message)

    def queue(self, command, data, callback=None):
        logger.info('queueing %s %s %s', command, type(data), str(callback))
        self._queue.put(Message(command, data, callback))

    def classify(self, message):
        classification = message.data
        if classification is not None:
            with self.control_lock:
                logger.info('classifying')
                subject = self.control.classify(classification)

                if subject is not None:
                    logger.info('responding with subject %s score %.4f',
                                str(subject.id), subject.score)
                    message.callback(subject)
                else:
                    logger.info('Already classified, not responding')
        else:
            logger.error('Classification was None: %s', str(classification))

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
        # Ensure thread doesn't exit
        # Wait for classifications in queue
        while not self.exit.is_set():

            message = self._queue.get()
            if message is not None:
                logger.debug('received message')
                try:
                    self.command(message)
                except Exception as e:
                    logger.error(e)
                    raise e
                    sys.exit(1)

        logger.warning('thread exiting')


class DualCursor:

    def __init__(self, cursor_1, cursor_2):
        self.cursors = (cursor_1, cursor_2)
        self.i = 0

    @property
    def cursor(self):
        return self.cursors[self.i]

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __len__(self):
        return sum(self.cursors, key=lambda cursor: cursor.getCount())

    def next(self):
        if self.i > 1:
            raise StopIteration

        try:
            return next(self.cursor)
        except StopIteration:
            logger.info('Switching cursors: %d', self.i)
            self.i += 1
            return self.next()
