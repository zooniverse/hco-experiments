
# Collection of infrastructures to run SWAP in an online state
# with Caesar

from swap.app.control import OnlineControl

import logging
from flask import Flask, request, jsonify

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


@app.route('/classify')
def classify():
    classification = OnlineControl.parse_classification(request.args)
    OnlineControl().classify(classification)

    return jsonify({})


def run():
    OnlineControl()
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    run()
