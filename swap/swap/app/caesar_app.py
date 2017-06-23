
# Collection of infrastructures to run SWAP in an online state
# with Caesar

from swap.app.control import OnlineControl
import swap.config as config

import logging
from flask import Flask, request, jsonify
import requests
import threading
from queue import Queue


logger = logging.getLogger(__name__)


# Actions we might take to notify caesar

# retire subject

# post score changes

# change subject workflow


# API so Caesar can notify us

# receive classification
"""
    Data required in extraction:
    unique user identifier (whether that's user_name or user_id)
    subject identifier (subject_id, object_id)
    annotation
    gold label
        Should we rely on Caesar to maintain gold labels for us?
        Do we need to push new gold labels to Caesor if so?
        Might be better to maintain them in our local db

    Should store the incoming classificadtion in our db
        Do we need validation checks to ensure we don't have
        duplicate classificationsin our db
    Should then recalculate scores

    Do we then need to respond with the updated for that subject?
        Would it be better to just send our own asynchronous
        retirement message when we see fit?
"""


"""
TODO:
    Write online controller
        Listen as reducer and process incoming classifications
        Pre-process classifications already in database
    Write request/response schema
    Write new database methods
        To store incoming classifications in cl database
"""

"""
To configure caesar:
    swap must be registered as an external extractor in caesar's config
    swap must be registered as an external reducer in caesar's config
        with no URL
"""

app = Flask(__name__)
threader = None


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    """
    Receive a classification as an extractor from Caesar
    """
    logger.info('received classification')
    logger.debug(str(request))

    # Parse json from request
    data = request.get_json()
    classification = OnlineControl.parse_classification(data)

    logger.debug(classification)
    logger.debug('sending classification to swap thread')
    threader.queue.put(classification)

    # return empty response

    resp = jsonify({'status': 'ok'})
    # resp.status_code = 200
    return resp


def generate_address():
    """
    Generate Caesar address to PUT reduction
    """
    s = config.caesar._addr_format
    c = config.caesar

    kwargs = {
        'host': c.host,
        'port': c.port,
        'workflow': c.response.workflow,
        'reducer': c.response.reducer
    }

    return s % kwargs


def respond(subject):
    """
    PUT subject score to Caesar
    """
    c = config.caesar

    address = generate_address()

    # address = 'http://localhost:3000'
    body = {
        'reduction': {
            'subject_id': subject.id,
            'data': {
                c.response.field: subject.score
            }
        }
    }

    print('responding!')
    logger.info('PUT subject %d score %.4f to caesar',
                subject.id, subject.score)

    requests.put(address, json=body)
    logger.debug('done')


def run():
    global threader
    threader = Threader(Queue())
    threader.start()

    c = config.caesar.swap
    app.run(host=c.bind, port=c.port, debug=c.debug)


class Threader(threading.Thread):

    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.exit = threading.Event()
        self.daemon = True

        self.control_lock = threading.Lock()
        self.control = OnlineControl()

    def run(self):
        """
        Main thread for processing classifications
        """

        # Ensure thread doesn't exit
        # Wait for classifications in queue
        while not self.exit.is_set():

            classification = self.queue.get()
            if classification is not None:

                self.process_message(classification)

        logger.warning('thread exiting')

    def process_message(self, classification):
        """
        Process a classification and PUT response to caesar
        """
        with self.control_lock:
            logger.info('classifying')
            subject = self.control.classify(classification)
            logger.info('responding with subject %s score %.4f',
                        subject.id, subject.score)

            respond(subject)


if __name__ == '__main__':
    run()
