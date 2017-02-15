################################################################
# User agent, keeps track of a user's history and
# score

from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.tracker import User_Score_Tracker as UTracker


class User(Agent):

    def __init__(self, user_name, epsilon):
        self.user_name = user_name
        self.epsilon = epsilon

        self.annotations = Tracker()
        self.gold_labels = Tracker()
        self.labels = {}

        self.prob_true = UTracker(1, self.epsilon)
        self.prob_false = UTracker(0, self.epsilon)

    def addClassification(self, cl):
        # Increment basic tracking
        annotation = int(cl['annotation'])
        gold = int(cl['gold_label'])

        self.annotations.add(annotation)
        self.gold_labels.add(gold)

        # Decide which tracker to user
        if gold == 1:
            prob = self.prob_true
        elif gold == 0:
            prob = self.prob_false

        # Add classification to tracker
        prob.add(annotation)

    def getHistory(self):
        pass

    def getCurrentScore(self):
        return -1
