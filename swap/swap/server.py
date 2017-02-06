################################################################
# Interface between the data structure and SWAP
# Serves data to SWAP

# Swap isn't ready yet for this to work, but this is the general
# outline of how server is going to interact with DB and SWAP

from swap import SWAP
from swap.mongo import DB

class Server:

    def __init__(self):
        self.db = DB()

    def process(self):
        data
        swap = SWAP("Args passed to swap")

    def getData(self):
        return self.db.classifications.getAllItems()
