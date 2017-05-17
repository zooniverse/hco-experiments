################################################################
#


class Ledger:
    def __init__(self):
        # unordered dictionary of all transactions in this ledger
        # Transactions are linked in order to allow downstream updating,
        # for example to update subject scores
        self.transactions = {}
        self.stale = True
        self.changed = []

    def change(self, id_):
        self.changed.append(id_)

    @property
    def score(self):
        if self.stale or self._score is None:
            self.recalculate()
        return self._score

    def add(self, transaction):
        id_ = transaction.id
        # Record the transactions order
        transaction.order = len(self.transactions)
        # Store this transaction
        self.transactions[id_] = transaction
        self.change(id_)

        self.stale = True

        return id_

    def get(self, id_):
        return self.transactions[id_]

    def recalculate(self):
        self.clear_changes()

    def clear_changes(self):
        self.stale = False
        self.changed = []

    def update(self, id_):
        self.stale = True
        self.change(id_)
        self.transactions[id_].notify()


class Transaction:
    def __init__(self, id_):
        self.id = id_
        self.order = None

    def notify(self):
        # Notify connected nodes that this transaction changed
        pass

    def __str__(self):
        s = 'id %s order %s' % (str(self.id), str(self.order))
        return s
