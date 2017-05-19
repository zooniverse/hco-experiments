################################################################
# Methods for experiment collection

from swap.db import DB

collection = DB().experiment
aggregate = collection.aggregate


def upload_trials(trials):
    data = [trial.db_export() for trial in trials]
    collection.insert_many(data)
