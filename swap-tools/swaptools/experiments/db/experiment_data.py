################################################################
# Methods for experiment collection

from swap.db import DB

collection = DB().experiment
aggregate = collection.aggregate


def upload_trials(trials, experiment_name):
    data = []
    for trial in trials:
        data += trial.db_export(experiment_name)

    collection.insert_many(data)
