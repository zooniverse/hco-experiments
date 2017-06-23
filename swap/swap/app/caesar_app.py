
# Collection of infrastructures to run SWAP in an online state
# with Caesar

from swap.app.control import OnlineControl

import logging
from flask import Flask, request, jsonify
import requests
import threading
from queue import Queue
import atexit


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

app = Flask(__name__)
threader = None


@app.route('/classify', methods=['GET', 'POST'])
def classify():
    print(1)
    logger.debug('received classification')
    logger.debug(str(request))
    print(request.method)
    print(dir(request))
    print(request.get_data())
    print(request.get_json())
    print(request.values)
    # print(request.get_json())

    # import code
    # code.interact(local=locals())
    classification = OnlineControl.parse_classification(request.get_json())
    print(classification)
    threader.queue.put(classification)

    resp = jsonify({'status': 'ok'})
    # resp.status_code = 200
    return resp


def respond(subject):
    address = 'localhost:3000/workflows/4373/reducers/swap/reductions'
    address = 'http://localhost:3000'
    body = {
        'reduction': {
            'subject_id': subject.id,
            'data': {
                'swap_score': subject.score
            }
        }
    }

    print('responding!')

    requests.put(address, json=body)


def run():
    global threader
    threader = Threader(Queue())
    threader.start()
    app.run(host='0.0.0.0', port=5000, debug=True)


class Threader(threading.Thread):

    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.exit = threading.Event()
        self.daemon = True

        self.control_lock = threading.Lock()
        self.control = OnlineControl()

    def run(self):
        while not self.exit.is_set():
            print(1)
            classification = self.queue.get()
            if classification is not None:
                print(1)
                self.process_message(classification)
        print('thread exiting')

    def process_message(self, classification):
        with self.control_lock:
            logger.info('classifying')
            subject = self.control.classify(classification)
            logger.info('responding with subject %s score %.4f',
                        subject.id, subject.score)

            respond(subject)


# @atexit.register
# def goodbye():
#     logger.info('Stopping threads')
#     global threader
#     print(threader.is_alive())
#     # print(threader.queue.qsize())
#     threader.exit.set()
#     threader.join()


if __name__ == '__main__':
    run()
