
# Collection of infrastructures to run SWAP in an online state
# with Caesar

from swap.app.control import ThreadedControl, OnlineControl
import swap.config as config

import logging
from flask import Flask, request, jsonify
import requests


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


class API:

    def __init__(self, control_thread):
        self.app = Flask(__name__)
        self.control = control_thread

    def run(self):
        self._route('/', 'scores', self.scores, ['GET'])
        self._route('/classify', 'classify', self.classify, ['POST'])
        self.app.run()

    def _route(self, route, name, func, methods=('GET')):
        self.app.add_url_rule(
            route, name, func, methods=methods)

    def get(self, subject):
        """
        Return current score of a subject
        """
        pass

    def classify(self):
        """
        Receive a classification from caesar and process it
        """
        logger.info('received classification')
        logger.debug(str(request))

        # Parse json from request
        data = request.get_json()
        classification = OnlineControl.parse_classification(data)

        logger.debug(classification)
        logger.debug('sending classification to swap thread')
        self.control.queue('classify', classification, respond)

        # return empty response

        resp = jsonify({'status': 'ok'})
        resp.status_code = 200
        return resp

    def scores(self):
        """
        Return current score export
        """
        scores = self.control.scores()

        return jsonify(scores.full_dict())


def generate_address():
    """
    Generate Caesar address to PUT reduction
    """
    s = config.online_swap._addr_format
    c = config.online_swap

    kwargs = {
        'host': c.caesar.host,
        'port': c.caesar.port,
        'workflow': c.workflow,
        'reducer': c.caesar.reducer
    }

    return s % kwargs


def respond(subject):
    """
    PUT subject score to Caesar
    """
    c = config.online_swap

    address = generate_address()

    # address = 'http://localhost:3000'
    body = {
        'reduction': {
            'subject_id': subject.id,
            'data': {
                c.caesar.field: subject.score
            }
        }
    }

    print('responding!')
    logger.info('PUT subject %d score %.4f to caesar',
                subject.id, subject.score)

    requests.put(address, json=body)
    logger.debug('done')


def init_threader(swap=None):
    thread = ThreadedControl(swap=swap)
    thread.start()

    return thread


# def run():
#     c = config.caesar.swap
#     app.run(host=c.bind, port=c.port, debug=c.debug)


if __name__ == '__main__':
    control = init_threader()
    api = API(control)
    api.run()
