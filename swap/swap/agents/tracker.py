################################################################
# Tracks probabilities as they change temporally


class Tracker:

    def __init__(self, value):
        self.history = [value]
        self.current = value

        self.n = len(self.history)

    def add(self, value):
        self.history.append(value)
        self.current = value

        self.n += 1

    def current(self):
        return self.current


class User_Score_Tracker:

    def __init__(self, label, epsilon):
        self.label = label
        self.epsilon = epsilon

        # FIXME @marco should these values be initialized
        # to epsilon or to zero/empty?
        self.n_seen = 0
        self.n_matched = 0

        Tracker.__init__(epsilon)

    def calculateScore(self):
        score = self.n_seen / self.n_matched

        return score

    def add(self, matched):
        self.n_seen += 1
        if matched:
            self.n_matched += 1

        score = self.calculateScore()
        Tracker.add(score)
