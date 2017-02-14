################################################################
# User agent, keeps track of a user's history and
# score

from swap.agents.agent import Agent


class User(Agent):

    def __init__(self, user_name, epsilon):
        self.user_name = user_name
        self.epsilon = epsilon

        self.annotations = []
        self.gold_labels = []
        self.labels = {}

        self.prob_true = Prob_Tracker(1, self.epsilon)
        self.prob_false = Prob_Tracker(0, self.epsilon)

        self.n_classified = 0

    def setEpsilon(self, epsilon):
        pass

    def addClassification(self, cl):
        # Increment basic tracking
        self.annotations.append(cl['annotation'])
        self.gold_labels.append(cl['gold_label'])
        self.n_classified += 1

        # Decide which tracker to user
        if cl['gold_label'] == 1:
            prob = prob_true
        elif cl['gold_label'] == 0:
            prob = prob_false

        # Add classification to tracker
        prob.addClassification(cl['annotation'])
        # Calculate and store new user probability
        prob.calculateScore()

    def getHistory(self):
        pass

    # TODO
    def getCurrentScore(self):
        return self.epsilon




