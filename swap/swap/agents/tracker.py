################################################################
# Tracks probabilities as they change temporally


class Tracker:

    def __init__(self, value=None):
        self._history = []
        self._current = value

        if value is not None:
            self._history.append(value)

        self.n = len(self._history)

    def add(self, value):
        self._history.append(value)
        self._current = value

        self.n += 1

    def current(self):
        return self._current

    def getHistory(self):
        return self._history[:]

    def size(self):
        return len(self._history)


class User_Score_Tracker(Tracker):

    def __init__(self, label, epsilon):
        super().__init__(epsilon)

        self.label = label
        self.epsilon = epsilon

        # FIXME @marco should these values be initialized
        # to epsilon or to zero/empty?
        # @Michael: Thats a matter of definition. In my view its either epsilon or empty.
        #           If I am thinking about plotting user histories I'd want epsilon to be 
        #              the start so it is easier to have epsilon in there.
        #           On the other hand, the user history has then one entry more than gold labels seen.
        #            If that is not a problem I would probably initialize with epsilon.
        self.n_seen = 0
        self.n_matched = 0

    def calculateScore(self):
        score = self.n_matched / self.n_seen

        return score

    def add(self, annotation):
        self.n_seen += 1

        if annotation == self.label:
            self.n_matched += 1

        score = self.calculateScore()
        super().add(score)


class Tracker_Collection:

    def __init__(self):
        self.trackers = {}

    def add(self, label, tracker):
        if label in self.trackers:
            raise NameError(
                'Tracker with that label already \
                exists! Remove it first')

        if type(tracker) is not tracker:
            raise ValueError

        self.trackers[label] = tracker

    def remove(self, label):
        if label in self.trackers:
            tracker = self.trackers[label]
            del self.trackers[label]

            return tracker

    def get(self, label):
        if label in self.trackers:
            return self.trackers[label]


class Labeled_Trackers:

    def __init__(self, tracker, labels, value=None):
        if type(labels) is not list:
            raise ValueError("Need list of labels to initialize trackers")

        self.trackers = {}

        for label in labels:
            self.add(tracker, label, value)

    def add(self, tracker_type, label, value):
        tracker = tracker_type(label, value)

        self.trackers[label] = tracker
        return tracker

    def get(self, label):
        return self.trackers[label]

    def getAll(self):
        return self.trackers
