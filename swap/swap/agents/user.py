################################################################
# User agent, keeps track of a user's history and
# score


from swap.agents.agent import Agent, MultiStat
from swap.agents.tracker import Tracker
from swap.agents.tracker import Tracker_Collection


class User(Agent):
    """
        Agent to manage subject scores
    """

    def __init__(self, user_name, epsilon):
        """
            Initialize a User Agent

            Args:
                user_id: (int) id number
                epsilon: (float) prior user probability
        """
        super().__init__(user_name, epsilon)

        self.gold_labels = Tracker()

        self.trackers = Tracker_Collection.Generate(
            User_Score_Tracker, [0, 1], epsilon)

        self.count = 0

    def addClassification(self, cl, gold):
        """
            adds a classification and calculates the new score

            Args:
                cl (dict) classification data from database
        """

        # Increment basic tracking
        annotation = int(cl.annotation)

        self.annotations.add(annotation)
        self.gold_labels.add(gold)

        # Decide which tracker to user
        tracker = self.trackers.get(gold)

        # Add classification to tracker
        tracker.add(annotation)

        self.count += 1

    def getScore(self, label):
        """
            Gets the current score from the tracker for the annotation

            Args:
                label (int) label of the tracker, i.e. the annotation
        """
        return self.trackers.get(label).current()

    def getCount(self):
        return self.count

    def export(self):
        """
            Exports Subject data

            Structure:
                'gold_labels': (list), history of subject gold labels
                'score_0': (int),      current bogus object score
                'score_1': (int),      current real object score
                'score_0_history':     history of score_0
                'score_1_history':     history of score_1
        """
        data = {
            'gold_labels': self.gold_labels.getHistory()
        }

        for label, tracker in self.trackers.getAll().items():
            score = 'score_%s' % str(label)
            history = 'score_%s_history' % str(label)

            data[score] = tracker.current()
            data[history] = tracker.getHistory()

        return data

    def __str__(self):
        return 'id: %s score 0: %.2f score 1: %.2f' % \
            (self.id, self.getScore(0), self.getScore(1))

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Users
        """
        data = []
        for i in [0, 1]:
            p = [agent.getScore(i) for agent in bureau]
            data.append((i, p))

        return MultiStat(*data)


class User_Score_Tracker(Tracker):
    """
        Modified tracker specifically for user scores
    """

    def __init__(self, label, epsilon):
        """
            Initialize a user score tracker

            Args:
                label: label for the tracker,
                       typically the annotation type
                epsilon: (float) initial user score value
        """
        super().__init__(epsilon)

        self.label = label
        self.epsilon = epsilon

        self.n_seen = 0
        self.n_matched = 0

    def calculateScore(self):
        n_matched = self.n_matched
        n_seen = self.n_seen

        # score = n_matched / n_seen

        # TODO: Idea with Bayesian Probability Update
        # Likelihood is Bernoulli distribution
        # Prior is Beta distribution (conjugate of Bernoulli)
        #  - we assume Beta(alpha=2,beta=2) distribution which has mode at 0.5
        # The posterior distribution is then also a Beta distribution with:
        # alpha_new = alpha + n_matched, beta_new = beta + n_seen - n_matched
        # the mode (most likely value) of a Beta distribution is then:
        # (alpha_new - 1) / (alpha_new + beta_new - 2)

        alpha = 2
        beta = 2
        alpha_new = alpha + n_matched
        beta_new = beta + n_seen - n_matched
        score = (alpha_new - 1) / (alpha_new + beta_new - 2)

        # TODO TEMPORARY FIX
        # Prevents a user from receiving a perfect 1.0 score
        # or a 0.0 score.
        # If the score is 1, then it is adjusted to:
        #   n
        # ------
        #  n+1
        # If the score is 0, then it is the complement of that:
        #       n
        # 1 - ------
        #      n+1

#        if score == 0:
#            score = 1 - (n_seen / (n_seen + 1))
#        elif score == 1:
#            score = n_seen / (n_seen + 1)

        return score

    def add(self, annotation):
        self.n_seen += 1

        if annotation == self.label:
            self.n_matched += 1

        score = self.calculateScore()
        super().add(score)
