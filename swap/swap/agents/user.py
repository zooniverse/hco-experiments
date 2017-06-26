################################################################
# User agent, keeps track of a user's history and
# score


from swap.agents.agent import Agent, MultiStat
import swap.agents.ledger as ledger
import swap.config as config


class User(Agent):
    """
        Agent to manage subject scores
    """

    class_name = 'user'

    def __init__(self, user_name):
        """
            Initialize a User Agent

            Args:
                user_id: (int) id number
                epsilon: (float) prior user probability
        """
        super().__init__(user_name, Ledger)

    def classify(self, cl, subject):
        """
            adds a classification and calculates the new score

            Args:
                cl (Classification) classification data from database
                subject (Subject)   relevant subject agent
        """
        if cl.user != self.id:
            raise ValueError(
                'Classification user name %s ' % str(cl.user) +
                'does not match my id %s' % str(self.id))
        annotation = cl.annotation

        if subject.id not in self.ledger.transactions:
            t = Transaction(subject, annotation)
            self.ledger.add(t)

    # def export(self):
    #     """
    #         Exports Subject data

    #         Structure:
    #             'gold_labels': (list), history of subject gold labels
    #             'score_0': (int),      current bogus object score
    #             'score_1': (int),      current real object score
    #             'score_0_history':     history of score_0
    #             'score_1_history':     history of score_1
    #     """
    #     raise DeprecationWarning
    #     data = {
    #         'gold_labels': self.gold_labels.getHistory()
    #     }

    #     for label, tracker in self.trackers.getAll().items():
    #         score = 'score_%s' % str(label)
    #         history = 'score_%s_history' % str(label)

    #         data[score] = tracker.current()
    #         data[history] = tracker.getHistory()

    #     return data

    def __str__(self):
        return 'id: %s score 0: %.2f score 1: %.2f' % \
            (self.id, *self.score)

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Users
        """

        p = [agent.score for agent in bureau]
        p = zip(*p)

        p0, p1 = p
        data = [(0, p0), (1, p1)]

        return MultiStat(*data)


# class User_Score_Tracker(Tracker):
#     """
#         Modified tracker specifically for user scores
#     """

#     def __init__(self, label, epsilon):
#         """
#             Initialize a user score tracker

#             Args:
#                 label: label for the tracker,
#                        typically the annotation type
#                 epsilon: (float) initial user score value
#         """
#         super().__init__(epsilon)

#         self.label = label
#         self.epsilon = epsilon

#         self.n_seen = 0
#         self.n_matched = 0

#     def calculateScore(self):
#         n_matched = self.n_matched
#         n_seen = self.n_seen

#         # score = n_matched / n_seen

#         # TODO: Idea with Bayesian Probability Update
#         # Likelihood is Bernoulli distribution
#         # Prior is Beta distribution (conjugate of Bernoulli)
#         #  - we assume Beta(alpha=2,beta=2) distribution which has mode at 0.5
#         # The posterior distribution is then also a Beta distribution with:
#         # alpha_new = alpha + n_matched, beta_new = beta + n_seen - n_matched
#         # the mode (most likely value) of a Beta distribution is then:
#         # (alpha_new - 1) / (alpha_new + beta_new - 2)

#         alpha = 2
#         beta = 2
#         alpha_new = alpha + n_matched
#         beta_new = beta + n_seen - n_matched
#         score = (alpha_new - 1) / (alpha_new + beta_new - 2)

#         # TODO TEMPORARY FIX
#         # Prevents a user from receiving a perfect 1.0 score
#         # or a 0.0 score.
#         # If the score is 1, then it is adjusted to:
#         #   n
#         # ------
#         #  n+1
#         # If the score is 0, then it is the complement of that:
#         #       n
#         # 1 - ------
#         #      n+1

# #        if score == 0:
# #            score = 1 - (n_seen / (n_seen + 1))
# #        elif score == 1:
# #            score = n_seen / (n_seen + 1)

#         return score

#     def add(self, annotation):
#         self.n_seen += 1

#         if annotation == self.label:
#             self.n_matched += 1

#         score = self.calculateScore()
#         super().add(score)


class Ledger(ledger.Ledger):
    def __init__(self, id_):
        super().__init__(id_)
        self.no = Counter()
        self.yes = Counter()

        self.recalculate()

    @ledger.Ledger.score.setter
    def score(self, new):
        if self._score != new:
            self._score = new

    def add(self, transaction):
        # Remove gold label from transaction, will be put back in when
        # recalculating
        transaction.gold = None
        id_ = super().add(transaction)

        if not config.back_update:
            self.recalculate()

        return id_

    def counter(self, gold):
        if gold == 0:
            return self.no
        elif gold == 1:
            return self.yes

    def action(self, transaction, version):
        t = transaction
        c = self.counter(t.gold)
        if c is not None:
            if version == 'new':
                if t.matched:
                    c.match()
                else:
                    c.see()
            elif version == 'old':
                if t.matched:
                    c.unmatch()
                else:
                    c.unsee()

    def recalculate(self):
        # print(self.changed)
        for i in self.changed:
            # print(i, self.id)
            t = self.transactions[i]

            if t.changed:
                self.action(t, 'old')
                t.commit_change()
                self.action(t, 'new')

                t.score = self._calculate()

        score = self._calculate()

        super().recalculate()

        self.score = score
        return score

    def _calculate(self):
        return (self.no.score, self.yes.score)


class Transaction(ledger.Transaction):
    def __init__(self, subject, annotation):
        super().__init__(subject, annotation)

        self.gold = None

        # TODO store current score

        self.notify(subject)

    def commit_change(self):
        self.gold = self.change

    def notify(self, agent):
        self.change = agent.gold

    @property
    def changed(self):
        return self.gold != self.change

    @property
    def matched(self):
        return self.annotation == self.gold

    def __str__(self):
        g = self.gold
        if g is None:
            g = -1

        s = super().__str__()
        s += ' gold %d score %s' % \
            (g, self.score)
        return s


class Counter:
    def __init__(self):
        self.seen = 0
        self.matched = 0

    def calculate(self):
        def formula(n, total):
            alpha = 2
            beta = 2
            alpha += n
            beta += total - n
            score = (alpha - 1) / (alpha + beta - 2)
            return score

        return formula(self.matched, self.seen)

    def unmatch(self):
        self.matched -= 1
        self.unsee()

    def unsee(self):
        self.seen -= 1

    def match(self):
        self.matched += 1
        self.see()

    def see(self):
        self.seen += 1

    @property
    def score(self):
        return self.calculate()
