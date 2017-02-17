################################################################
# Subject agent, keeps track of a subject's history and
# score

from swap.agents.tracker import Tracker
from swap.agents.agent import Agent


class Subject(Agent):
    """
        Agent to manage subject scores
    """

    def __init__(self, subject_id, p0):
        # initialize Agent class
        super().__init__(subject_id, p0)

        # self.name = subject_id
        # self.p0 = p0

        # Initialize trackers
        self.annotations = Tracker()
        self.user_scores = Tracker()

        self.tracker = Tracker(p0)

    def addClassification(self, cl, user_agent):
        """
            adds a classification and calculates the new score

            Args:
                cl (dict) classification data from database
                user_agent (Agent->User)  Agent for the classifying user
        """
        annotation = int(cl['annotation'])
        s_score = self.getScore()
        u_score = user_agent.getScore(annotation)

        self.annotations.add(annotation)
        self.user_scores.add(u_score)

        # Get user's 1 and 0 scores
        # TODO @marco I'm not sure of what you added
        # to the main swap code last night (2/14/17)
        u_score_1 = user_agent.getScore(1)
        u_score_0 = user_agent.getScore(0)
        # s_score already defined ^^^

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
            a = s_score * (1-u_score_1)
            b = 1 - s_score
            c = u_score_0

        score = a / (a + b*c)
        return score
