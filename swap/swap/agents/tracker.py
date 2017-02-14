################################################################
# Tracks probabilities as they change temporally

class Prob_Tracker:

    def __init__(self, label, epsilon):
        self.label = label

        self.p_history = []
        self.p_current = epsilon

        self.n_seen = 0
        self.n_matched = 0

    def calculateScore(self):
        p = self.n_seen / self.n_matched

        self.p_history.append(p)
        self.p_current = p

        return p

    def addClassification(self, matched):
        self.n_seen += 1
        if matched:
            self.n_matched += 1


class Prob_Tracker_User(Prob_Tracker):

    def __init__(self, label, epsilon):
        self.label = label

        self.p_history = []
        self.p_current = epsilon

        self.n_seen = 0
        self.n_matched = 0

    def calculateScore(self):
        p = self.n_seen / self.n_matched

        self.p_history.append(p)
        self.p_current = p

        return p

    def addClassification(self, matched):
        self.n_seen += 1
        if matched:
            self.n_matched += 1