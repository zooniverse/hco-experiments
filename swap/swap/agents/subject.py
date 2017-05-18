################################################################
# Subject agent, keeps track of a subject's history and
# score

from swap.agents.tracker import Tracker
from swap.agents.agent import Agent
import swap.agents.ledger as ledger
from swap.config import Config


class Subject(Agent):
    """
        Agent to manage subject scores
    """

    def __init__(self, subject_id, gold_label=-1):
        """
            Initialize a Subject Agent

            Args:
                subject_id:  (int) id number
                gold_label: (int)
                    -1 no gold label
                     0 bogus object
                     1 real supernova
        """
        super().__init__(subject_id, Ledger)
        # store gold label
        self._gold = gold_label

    # @score.setter
    # def score(self, score):
    #     self.tracker.add(score)

    # @property
    # def label(self):
    #     """
    #         Gets the current label of the subject based on its score
    #     """
    #     if self.score > 0.5:
    #         return 1
    #     else:
    #         return 0

    @property
    def gold(self):
        return self._gold

    def classify(self, cl, user):
        """
            adds a classification and calculates the new score

            Args:
                cl (Classification) classification data from database
                user_agent (Agent->User)  Agent for the classifying user
        """
        if cl.subject != self.id:
            raise ValueError(
                'Classification subject id %s ' % str(cl.subject) +
                'does not match my id %s' % str(self.id))
        annotation = int(cl.annotation)
        id_ = user.id

        t = Transaction(id_, user, annotation)
        self.ledger.add(t)

    def set_gold_label(self, gold_label):
        """
            Set a subject's gold label

            Args:
                gold_label: (int)
                    -1 no gold label
                     0 bogus object
                     1 real supernova
        """
        self._gold = gold_label

    def isgold(self):
        return self.gold in [0, 1]

    def export(self):
        raise DeprecationWarning
        """
            Exports Subject data

            Structure:
                'user_scores': (list), history of user scores
                'score': (int),        current subject score
                'history': (list),     score history
                'label': (int),        current subject label
                'gold_label' (int),    current subject gold label
        """
        data = {
            'subject_id': self.id,
            'user_scores': self.user_scores.getHistory(),
            'score': self.tracker.current(),
            'history': self.tracker.getHistory(),
            'label': self.label,
            'gold_label': self.gold
        }

        return data

    def __str__(self):
        return 'id: %s score: %.2f gold label: %d' % \
            (self.id, self.score, self.gold)


class Ledger(ledger.Ledger):
    def __init__(self):
        super().__init__()
        # First change in the change cascade
        # self.first_change = None
        # Most recently added transaction
        self.last = None
        self._score = None
        # Note: first_change and last are references to the
        #       actual transactions, not their id numbers

    def recalculate(self):
        transaction = self.first_change

        if transaction is None:
            score = Config().p0
        else:
            score = transaction.get_prior()
            while transaction is not None:
                score = transaction.calculate(score)
                transaction = transaction.right

            super().recalculate()

        self._score = score
        return score

    def add(self, transaction):
        # Link last transaction to this one
        if self.last is not None:
            self.last.right = transaction
            transaction.left = self.last

        # Store this transaction
        id_ = super().add(transaction)

        # Determine if most first change in cascade
        # self._change(transaction)
        # Assign this as last added
        self.last = transaction

        return id_

    @property
    def first_change(self):
        if len(self.changed) == 0:
            return None

        def order(id_):
            return self.transactions[id_].order
        id_ = min(self.changed, key=order)

        return self.transactions[id_]

    # def _change(self, transaction):
    #     """
    #         Determine which transaction changed first in the ledger
    #     """
    #     # Usefule when recalculating a subject score, for example, as
    #     # that needs to be calculated in order

    #     if self.first_change is None:
    #         self.first_change = transaction
    #     else:
    #         old = self.first_change.order
    #         new = transaction.order

    #         if new < old:
    #             self.first_change = transaction


class Transaction(ledger.Transaction):
    def __init__(self, id_, user, annotation):
        super().__init__(id_)
        self.user = user
        self.annotation = annotation
        self.score = None

        self.right = None
        self.left = None

    def notify(self):
        self.user.ledger.update(self.id)

    def get_prior(self):
        if self.left is None:
            return Config().p0
        else:
            return self.left.score

    def calculate(self, prior):
        # Calculation when annotation 1
        #           s*u1
        # -------------------------
        #    s*u1 + (1-s)*(1-u0)

        # Calculation when annotation 0
        #           s*(1-u1)
        # -------------------------
        #    s*(1-u1) + (1-s)*u0

        u0, u1 = self.user.score
        if self.annotation == 1:
            a = prior * u1
            b = (1 - prior) * (1 - u0)
        elif self.annotation == 0:
            a = prior * (1 - u1)
            b = (1 - prior) * (u0)

        # Preliminary catch of zero division error
        # TODO: Figure out how to handle it
        try:
            score = a / (a + b)
        # leave score unchanged
        except ZeroDivisionError as e:
            print(e)
            score = prior

        self.score = score
        return score

    def __str__(self):
        s = super().__str__()
        s += ' user %d annotation %d score %s' % \
            (self.id, self.annotation, self.score)
        return s
