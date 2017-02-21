################################################################
# User agent, keeps track of a user's history and
# score

from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.tracker import User_Score_Tracker as UTracker
from swap.agents.tracker import Labeled_Trackers


class User(Agent):
    """
        Agent to manage subject scores
    """

    def __init__(self, user_name, epsilon):

        # initialize Agent class
        super().__init__(user_name, epsilon)

        self.gold_labels = Tracker()

        self.trackers = Labeled_Trackers(UTracker, [0, 1], epsilon)

    def addClassification(self, cl):
        """
            adds a classification and calculates the new score

            Args:
                cl (dict) classification data from database
        """

        # Increment basic tracking
        annotation = int(cl['annotation'])
        gold = int(cl['gold_label'])

        self.annotations.add(annotation)
        self.gold_labels.add(gold)

        # Decide which tracker to user
        tracker = self.trackers.get(gold)

        # Add classification to tracker
        tracker.add(annotation)

    def getHistory(self):
        pass

    def getScore(self, label):
        """
            Gets the current score from the tracker for the annotation
            Args:
                label (int) label of the tracker, i.e. the annotation
        """
        return self.trackers.get(label).current()
