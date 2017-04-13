################################################################
# Subject agent, keeps track of a subject's history and
# score

from swap.agents.tracker import Tracker
from swap.agents.agent import Agent


class Subject(Agent):
    """
        Agent to manage subject scores
    """

    def __init__(self, subject_id, p0, gold_label=-1):
        """
            Initialize a Subject Agent

            Args:
                subjec_id:  (int) id number
                p0:         (float) prior subject probability
                gold_label: (int)
                    -1 no gold label
                     0 bogus object
                     1 real supernova
        """
        super().__init__(subject_id, p0)

        # Initialize trackers
        self.user_scores = Tracker()

        self.tracker = Tracker(p0)

        # store gold label
        self.gold_label = gold_label

    def addClassification(self, cl, user_agent):
        """
            adds a classification and calculates the new score

            Args:
                cl (dict) classification data from database
                user_agent (Agent->User)  Agent for the classifying user
        """
        annotation = int(cl.annotation)
        s_score = self.getScore()

        # Get user's 1 and 0 scores
        # TODO @marco I'm not sure of what you added
        # to the main swap code last night (2/14/17)
        u_score_1 = user_agent.getScore(1)
        u_score_0 = user_agent.getScore(0)

        self.annotations.add(annotation)
        self.user_scores.add((u_score_1, u_score_0))

        # calculate new score
        score = self.calculateScore(annotation, u_score_0,
                                    u_score_1, s_score)

        # add score to tracker
        self.tracker.add(score)

    def getHistory(self):
        # I'm envioning this for diagnostics and making the plots
        # for experiments, but not sure what this will entail
        pass

    def getLabel(self):
        """
            Gets the current label of the subject based on its score
        """
        if self.getScore() > 0.5:
            return 1
        else:
            return 0

    def getGoldLabel(self):
        """ Returns the gold label of the subject """
        return self.gold_label

    def setGoldLabel(self, gold_label):
        """
            Set a subject's gold label

            Args:
                gold_label: (int)
                    -1 no gold label
                     0 bogus object
                     1 real supernova
        """
        self.gold_label = gold_label

    def getScore(self):
        """
            Gets the current score from the tracker
        """
        return self.tracker.current()

    def calculateScore(self, annotation, u_score_0, u_score_1, s_score):
        """
            Calculates the new score based on the user scores and current
            subject score.

            Args:
                u_score_0: User's score for annotation 0
                u_score_1: User's score for annotation 1
                s_score: Subject's current score

            Calculation notes:
                s: subject score
                u1: user probability annotates 1
                u0: user probability annotates 0

                Calculation when annotation 1
                          s*u1
                -------------------------
                s*u1 + (1-u0)*(1-s)


                Calculation when annotation 0
                          s (1-u1)
                -------------------------
                s*(1-u1) + u0*(1-s)

        """
        if annotation == 1:
            a = s_score * u_score_1
            b = 1 - u_score_0
            c = 1 - s_score

        elif annotation == 0:
            a = s_score * (1 - u_score_1)
            b = 1 - s_score
            c = u_score_0
        # Preliminary catch of zero division error
        # TODO: Figure out how to handle it
        try:
            score = a / (a + b * c)
        # leave score unchanged
        except ZeroDivisionError as e:
            print(e)
            score = s_score

        return score

    def export(self):
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
            'label': self.getLabel(),
            'gold_label': self.getGoldLabel()
        }

        return data

    def __str__(self):
        return 'id: %s score: %.2f gold label: %d' % \
            (self.id, self.getScore(), self.getGoldLabel())
