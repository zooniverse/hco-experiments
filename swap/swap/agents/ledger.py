################################################################
#

import logging
logger = logging.getLogger(__name__)


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

    # TODO
    # Make sure back_update works properly with this setup!
    # Naiive recalculate vs real recalculate...
    # Logic for reclassification needs to be in the higher levels
    # in order to provide bureaus at the appropriate time

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

        self._score = None

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
        # if self.stale or self._score is None:
        #     raise StaleException(self)
        return self._score

    def add(self, transaction):
        """
        Add a transaction to the ledger
        """
        id_ = transaction.id
        # Record the transactions order
        transaction.order = len(self.transactions)

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

    def notify_agents(self, this_bureau, other_bureau):
        """
        This agent notifies all connected agents of a change

        If this ledger is part of a user, this ledger notifies all subjects
        that this user's score has changed.
        """
        # TODO

        for t in self:
            agent = t.agent(other_bureau)
            agent.ledger.notify(self.id, this_bureau)
            # t.notify(self.id)

    def notify(self, id_, bureau):
        """
        Notify this agent that the connected agent has changed

        If this ledger is part of a subject, the connected user agent
        is notifying the subject that its score has changed.
        """
        agent = bureau.get(id_)
        self.update(id_)
        self.transactions[id_].notify(agent)

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


class MissingReference(AttributeError):
    """
    Missing a reference to an object that should be there.
    """
    pass


class Transaction:
    """
    Records an interaction from an agent with this ledger
    """

    def __init__(self, agent, annotation):
        self.id = agent.id
        self.annotation = annotation
        # stores the order this transaction has in the ledger
        self.order = None
        self.score = None
        self.change = None

    def agent(self, bureau):
        return bureau.get(self.id)

    def notify(self, agent):
        pass

    def commit_change(self):
        pass

    def __str__(self):
        id_ = self.id
        if type(id_) is str and 'not-logged-in' in id_:
            id_ = id_.split('-')[-1]
        if self.order is None:
            self.order = -1
        s = 'id %20s order %2d annotation %d' % \
            (str(id_), self.order, self.annotation)
        return s


class StaleException(Exception):

    def __init__(self, ledger):
        msg = 'Ledger is stale: %s' % str(ledger)
        # logger.error(msg)
        super().__init__(msg)
        self.ledger = ledger
