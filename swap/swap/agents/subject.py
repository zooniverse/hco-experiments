################################################################
# Subject agent, keeps track of a subject's history and
# score

from swap.agents.agent import Agent
import swap.agents.ledger as ledger
import swap.config as config

import logging
logger = logging.getLogger(__name__)


class Subject(Agent):
    """
        Agent to manage subject scores
    """

    class_name = 'subject'

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

        if id_ not in self.ledger.transactions:
            t = Transaction(user, annotation)
            self.ledger.add(t)

    def set_gold_label(self, gold_label, subjects, users):
        """
            Set a subject's gold label

            Args:
                gold_label: (int)
                    -1 no gold label
                     0 bogus object
                     1 real supernova
        """
        old = self._gold
        new = gold_label

        if old != new:
            self._gold = gold_label
            self.ledger.notify_agents(subjects, users)

    def isgold(self):
        return self.gold in [0, 1]

    # def export(self):
    #     raise DeprecationWarning
    #     """
    #         Exports Subject data

    #         Structure:
    #             'user_scores': (list), history of user scores
    #             'score': (int),        current subject score
    #             'history': (list),     score history
    #             'label': (int),        current subject label
    #             'gold_label' (int),    current subject gold label
    #     """
    #     data = {
    #         'subject_id': self.id,
    #         'user_scores': self.user_scores.getHistory(),
    #         'score': self.tracker.current(),
    #         'history': self.tracker.getHistory(),
    #         'label': self.label,
    #         'gold_label': self.gold
    #     }

    #     return data

    def __str__(self):
        score = self.score
        if score is None:
            score = -1.

        return 'id: %s score: %.2f gold label: %d' % \
            (self.id, score, self.gold)


class Ledger(ledger.Ledger):
    def __init__(self, id_):
        super().__init__(id_)
        # First change in the change cascade
        # self.first_change = None
        # Most recently added transaction
        self.last = None
        # Note: first_change and last are references to the
        #       actual transactions, not their id numbers

    def recalculate(self):

        transaction = self.first_change

        if transaction is None:
            # Assume nothing has changed since last backupdate
            if len(self.transactions) == 0:
                # nothing has changed and there are no transactions
                # score is prior
                score = config.p0
            else:
                # nothing has changed and there are transactions
                # score is current score
                score = self._score
        else:
            prior = transaction.get_prior()
            while transaction is not None:
                transaction.commit_change()

                prior = transaction.calculate(prior)
                transaction = transaction.right

            score = prior

        self._score = score
        super().recalculate()
        return score

    def add(self, transaction):
        if transaction.id in self.transactions:
            return None

        # Link last transaction to this one
        if self.last is not None:
            self.last.right = transaction
            transaction.left = self.last

        # Store this transaction
        id_ = super().add(transaction)

        if not config.back_update:
            self._score = transaction.calculate()
            # TODO
            # calculate new score
            # but not by calling recalcluate

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
    def __init__(self, user, annotation):
        super().__init__(user, annotation)

        self.user_score = None
        self.right = None
        self.left = None

        self.notify(user)
        self.commit_change()

    def commit_change(self):
        self.user_score = self.change

    def notify(self, agent):
        try:
            self.change = agent.score
        except ledger.StaleException:
            # ledger is stale, continuing by using stale score
            # for now
            self.change = agent.ledger._score

    def get_prior(self):
        if self.left is None:
            return config.p0
        return self.left.score

    def calculate(self, prior=None):
        # Calculation when annotation 1
        #           s*u1
        # -------------------------
        #    s*u1 + (1-s)*(1-u0)

        # Calculation when annotation 0
        #           s*(1-u1)
        # -------------------------
        #    s*(1-u1) + (1-s)*u0

        if prior is None:
            prior = self.get_prior()
        u0, u1 = self.user_score

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
            logger.error(e)
            score = prior

        self.score = score
        return score

    def __str__(self):
        score = self.score
        if score is None:
            score = -1

        s = super().__str__()
        s += ' score %.5f user_score %.3f %.3f' % \
            (score, self.user_score[0], self.user_score[1])
        return s
