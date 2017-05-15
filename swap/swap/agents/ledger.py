################################################################
#


class Ledger:
    def __init__(self):
        # unordered dictionary of all transactions in this ledger
        # Transactions are linked in order to allow downstream updating,
        # for example to update subject scores
        self.transactions = {}
        # First change in the change cascade
        self.first_change = None
        # Most recently added transaction
        self.last = None

        # Note: first_change and last are references to the
        #       actual transactions, not their id numbers

    def recalculate(self):
        self.first_change = None

    @property
    def score(self):
        pass

    def add(self, transaction):
        # Link last transaction to this one
        if self.last is not None:
            self.last.right = transaction
            transaction.left = self.last

        # Store this transaction
        id_ = transaction.id
        transaction.order = len(self.transactions)
        self.transactions[id_] = transaction

        # Determine if most first change in cascade
        self._change(transaction)
        # Assign this as last added
        self.last = transaction

    def update(self, id_, update_function):

        # Update the transaction
        transaction = self.transactions[id_]
        update_function(transaction)

        # Update cascade
        self.transactions[id_] = transaction
        self._change(transaction)

    def _change(self, transaction):
        """
            Determine which transaction changed first in the ledger
        """
        # Usefule when recalculating a subject score, for example, as
        # that needs to be calculated in order

        if self.first_change is None:
            self.first_change = transaction
        else:
            old = self.first_change.order
            new = transaction.order

            if new < old:
                self.first_change = transaction


class Transaction:
    def __init__(self, id_):
        self.id = id_
        self.order = None
        self.right = None
        self.left = None
