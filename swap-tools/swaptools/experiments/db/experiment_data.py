################################################################
# Methods for experiment collection

from swaptools.experiments.db import DB

collection = DB().data
aggregate = collection.aggregate


def upload_trials(trials, experiment_name):
    data = []
    for trial in trials:
        data += trial.db_export(experiment_name)

    collection.insert_many(data)
