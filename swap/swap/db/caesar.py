
from swap.db.classifications import Classifications

import logging
logger = logging.getLogger(__name__)

class CaesarClassifications(Classifications):

    @staticmethod
    def _collection_name():
        return 'caesar_classifications'

    #######################################################################
