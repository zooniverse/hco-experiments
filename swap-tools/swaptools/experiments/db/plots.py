
from swaptools.experiments.db import DB

import logging
logger = logging.getLogger(__name__)

collection = DB().plots


def aggregate(*args, **kwargs):
    try:
        logger.debug(*args, **kwargs)
        return collection.aggregate(*args, **kwargs)
    except Exception as e:
        logger.error(e)
        raise e


def upload_plot(name, plot_points):
    data = []
    for point in plot_points:
        item = {'name': name, 'data': point}
        data.append(item)

    logger.debug('uploading plot')
    if len(data) > 0:
        collection.insert_many(data)
    logger.debug('done')


def get_plot(name):
    data = []

    logger.info('getting plot %s', name)
    cursor = collection.find({'name': name})

    for item in cursor:
        data.append(item['data'])

    return data
