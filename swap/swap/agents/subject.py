################################################################
# Subject agent, keeps track of a subject's history and
# score


class Subject(Agent):

    def __init__(self, subject_id, p0):
        self.name = subject_id
        self.p0 = p0

        self.annotations = []
        self.user_probabilities = []
        self.labels = {}

        self.prob_true = Prob_Tracker.Subject(1, self.p0)
        self.prob_false = Prob_Tracker.Subject(0, self.p0)

        self.current_label = None
        self.current_score = self.p0
        self.max_prob_history = [self.p0]

        self.n_seen = 0

    def addClassification(self, cl, user_agent):
        annotation = int(cl['annotation'])
        s_score = self.getScore()
        u_score = user_agent.getScore(annotation)

        self.annotations.append(annotation)
        self.user_scores.append(u_score)
        self.n_seen += 1

        u_score_1 = user_agent.getScore(1)
        u_score_0 = user_agent.getScore(0)
        # s_score already defined ^^^

        score = self.calculateScore(annotation, u_score_0,
                                    u_score_1, s_score)

        self.tracker.add(score)




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
