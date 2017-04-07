################################################################
# User agent, keeps track of a user's history and
# score

from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.tracker import User_Score_Tracker as UTracker
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
            UTracker, [0, 1], epsilon)

        self.count = 0

    def addClassification(self, cl):
        """
            adds a classification and calculates the new score

            Args:
                cl (dict) classification data from database
        """

        # Increment basic tracking
        annotation = int(cl.annotation)
        gold = int(cl.gold())

        self.annotations.add(annotation)
        self.gold_labels.add(gold)

        # Decide which tracker to user
        tracker = self.trackers.get(gold)

        # Add classification to tracker
        tracker.add(annotation)

        self.count += 1

    def getHistory(self):
        pass

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
