################################################################
# Subject agent, keeps track of a subject's history and
# score

from swap.agents.tracker import Tracker


class Subject(Agent):

    def __init__(self, subject_id, p0):
        self.name = subject_id
        self.p0 = p0

        self.annotations = Tracker()
        self.user_scores = Tracker()

        self.tracker = Tracker(p0)

    def addClassification(self, cl, user_agent):
        annotation = int(cl['annotation'])
        s_score = self.getScore()
        u_score = user_agent.getScore(annotation)

        self.annotations.add(annotation)
        self.user_scores.add(u_score)

        u_score_1 = user_agent.getScore(1)
        u_score_0 = user_agent.getScore(0)
        # s_score already defined ^^^

        score = self.calculateScore(annotation, u_score_0,
                                    u_score_1, s_score)

        self.tracker.add(score)

    def getHistory(self):
        pass

    def getLabel(self):
        if self.getScore() > 0.5:
            return 1
        else:
            return 0

    def getScore(self):
        return self.tracker.current()

    def calculateScore(annotation, u_score_0, u_score_1, s_score):
        """
            s: subject score
            u1: user probability annotates 1
            u0: user probability annotates 0

            Calculation when annotation 1
                      s*u1
            -------------------------
            s*u1 (s*u1 + (1-u0)*(1-s))


            Calculation when annotation 0
                      s (1-u1)
            -------------------------
            s*(1-u1) (s*(1-u1) + u0*(1-s))
        """
        if annotation == 1:
            a = s_score * u_score_1
            b = 1 - u_score_0
            c = 1 - s_score

        elif annotation == 0:
            a = s_score * (1 - u_score_1)
            b = u_score_0
            c = 1 - s_score

        score = a / (a + (b * c))
        return score
