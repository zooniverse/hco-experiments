################################################################
#


class Ledger:
    """
    Data structure used in an agent to keep track of all interactions
    with the agent

    Uses dynamic references inside the transactions to directly link each
    transaction to the acting agent. For example, each transaction in a ledger
    for a subject will have a reference to the user making the classification

    This allows quick recalculations as the ledger has direct access to
    the memory location of the relevant agent. This ledger is also intended
    for use with online bureaus to reduce memory load, and can dereference
    agents and rebuild reference trees arbitrarily from a bureau
    """

    def __init__(self, id_):
        """
        Args:
            id_: id of the agent this ledger belongs to
        """

        self.id = id_
        # unordered dictionary of all transactions in this ledger
        # the ordering is stored in the transactions, but is not necessary
        # for most ledger operations; mostly just useful for logging
        # and debugging
        self.transactions = {}

        self.stale = True
        self.bureau = None
        self.changed = []

    def set_bureau(self, bureau):
        """
        Provides a bureau to the ledger so it can rebuild agent references
        in its transactions on the fly. If this is a user ledger, provide a
        subject bureau and vice versa
        """
        self.bureau = bureau

    def _change(self, id_):
        """
        Mark a transaction as having changed
        """
        self.changed.append(id_)

    @property
    def score(self):
        """
        Get the current score from the ledger
        Recalculates the score if this ledger is stale
        """
        if self.stale or self._score is None:
            self.recalculate()
        return self._score

    def add(self, transaction):
        """
        Add a transaction to the ledger
        """
        id_ = transaction.id
        # Record the transactions order
        transaction.order = len(self.transactions)
        # Provide the transaction with a callback function to
        # rebuild its agent reference
        transaction.set_restore_callback(
            lambda: self.restore_agent(transaction.id))
        # Store this transaction
        self.transactions[id_] = transaction

        # Mark this change
        self._change(id_)
        self.stale = True

        return id_

    def get(self, id_):
        """
        Get a transaction from the ledger
        """
        return self.transactions[id_]

    def recalculate(self):
        """
        Calculate the new score given what has changed
        """
        # Clear the record of changes
        self.clear_changes()

    def notify_agents(self):
        """
        Have all transactions notify the connected agents
        that this agent has changed
        """
        for t in self:
            t.notify(self.id)

    def clear_changes(self):
        """
        Clear the record of changes
        """
        self.stale = False
        self.changed = []

    def update(self, id_):
        """
        Mark a transaction that has changed
        """
        self.stale = True
        self._change(id_)
        # self.transactions[id_].notify()

    def nuke(self):
        """
        Nuke this ledger. Delete all references to this agent in all
        the connected transactions
        """
        for t in self:
            t.agent.ledger.delrefs(self.id)

    def delrefs(self, id_):
        """
        Delete references to agent with id_ in this ledger
        """
        self.get(id_).delref()

    def delete_all_agents(self):
        """
        Delete all agent references in the transactions
        """
        for t in self:
            t.agent = None

    def restore_agent(self, id_):
        """
        Restore agent reference in transaction with id_
        """
        if self.bureau is None:
            raise MissingReference('Missing reference to bureau!')

        self.transactions[id_].restore(self.bureau.get(id_, make_new=False))

    def __str__(self):
        s = 'id %s transactions %d stale %s score %s\n' % \
            (str(self.id), len(self.transactions),
             str(self.stale), str(self._score))
        for t in sorted(self.transactions.values(), key=lambda t: t.order):
            s += '%s\n' % str(t)

        return s

    def __repr__(self):
        s = 'id %s transactions %d stale %s score %s\n' % \
            (str(self.id), len(self.transactions),
             str(self.stale), str(self._score))

        return s

    def __iter__(self):
        return iter(self.transactions.values())

    def __len__(self):
        return len(self.transactions)

    def __getstate__(self):
        self.bureau = None
        return self.__dict__.copy()

    def __setstate__(self, d):
        self.__dict__ = d

        def restore(transaction):
            def f():
                self.restore_agent(transaction.id)
            return f

        for t in self:
            t.set_restore_callback(restore(t))


class MissingReference(AttributeError):
    """
    Missing a reference to an object that should be there.
    """
    pass


class Transaction:
    """
    Records an interaction from an agent with this ledger
    """
    def __init__(self, id_, agent):
        self.id = id_
        self._agent = agent
        # stores the order this transaction has in the ledger
        self.order = None
        # a callback to restore the agent reference
        self.restore_callback = None

    @property
    def agent(self):
        """
        Restores the agent reference if it is missing
        """
        if self._agent is None:
            if self.restore_callback is None:
                raise MissingReference()
            else:
                self.restore_callback()
        return self._agent

    @agent.setter
    def agent(self, agent):
        self._agent = agent

    def notify(self, id_):
        """
        Notify connected nodes that this transaction changed
        """
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

    def set_restore_callback(self, callback):
        """
        A callback function to restore the agent reference
        """
        self.restore_callback = callback

    def __str__(self):
        id_ = self.id
        if type(id_) is str and 'not-logged-in' in id_:
            id_ = id_.split('-')[-1]
        if self.order is None:
            self.order = -1
        s = 'id %20s order %2d' % (str(id_), self.order)
        return s

    def __getstate__(self):
        self.agent = None
        self.restore_callback = None
        return self.__dict__.copy()
