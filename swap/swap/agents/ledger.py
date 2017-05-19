################################################################
#


class Ledger:
    def __init__(self, id_):
        # unordered dictionary of all transactions in this ledger
        # Transactions are linked in order to allow downstream updating,
        # for example to update subject scores
        self.id = id_
        self.transactions = {}
        self.stale = True
        self.bureau = None
        self.changed = []

    def set_bureau(self, bureau):
        self.bureau = bureau

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
        # self.transactions[id_].notify()

    def nuke(self):
        """
        Delete all references to the parent agent
        """
        for t in self:
            t.agent.ledger.delrefs(self.id)

    def delrefs(self, id_):
        """
        Delete references to agent with id_ in this ledger
        """
        self.get(id_).delref()

    def restore_agent(self, id_):
        self.transactions[id_].restore(self.bureau.get(id_))

    def __str__(self):
        s = 'transactions %d stale %s score %s\n' % \
            (len(self.transactions), str(self.stale), str(self._score))
        for t in sorted(self.transactions.values(), key=lambda t: t.order):
            s += '%s\n' % str(t)

        return s

    def __iter__(self):
        return iter(self.transactions.values())

    def __len__(self):
        return len(self.transactions)


class Transaction:
    def __init__(self, id_, agent):
        self.id = id_
        self.agent = agent
        self.order = None

    def notify(self, id_):
        # Notify connected nodes that this transaction changed
        self.agent.ledger.update(id_)

    def delref(self):
        """
        Remove references to relevant agent
        """
        self.agent = None

    def restore(self, agent):
        """
        Restore a reference to an agent
        """
        self.agent = agent

    def __str__(self):
        id_ = self.id
        if type(id_) is str and 'not-logged-in' in id_:
            id_ = id_.split('-')[-1]
        s = 'id %20s order %2d' % (str(id_), self.order)
        return s

    def __getstate__(self):
        return self.__dict__.copy()
