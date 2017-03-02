################################################################
# Test functions for tracker classes

from swap.agents.tracker import *


class Test_Tracker:
    def test_init(self):
        t = Tracker()

        assert type(t._history) is list
        assert t._current is None
        assert t.n == 0

    def test_init_value(self):
        t = Tracker(.5)

        assert type(t._history) is list
        assert t._history == [.5]
        assert t._current is .5
        assert t.n == 1

    def test_add(self):
        t = Tracker()
        t.add(.5)

        assert t._history == [.5]
        assert t._current == .5
        assert t.n == 1

    def test_add_many(self):
        t = Tracker()
        items = [1, 2, 3, 4, 5]
        for i in items:
            t.add(i)

        assert t._history == items
        assert t._current == 5
        assert t.n == 5

    def test_get_current(self):
        t = Tracker()
        items = [5, 4, 3, 2, 1]
        for i in items:
            t.add(i)

        assert t.current() == 1

    def test_size(self):
        t = Tracker()
        for i in range(10):
            t.add(i)
        assert t.size() == 10

    def test_getHistory(self):
        t = Tracker()
        for i in range(10):
            t.add(i)

        assert t.getHistory() == list(range(10))


class Test_User_Score_Tracker:

    def test_init(self):
        t = User_Score_Tracker(199, 101)

        assert t.label == 199
        assert t.epsilon == 101
        assert t.n_seen == 0
        assert t.n_matched == 0

    def test_calculcate_score(self):
        t = User_Score_Tracker(0, 0)
        t.n_seen = 100
        t.n_matched = 40

        assert t.calculateScore() == .4

    def test_0_add_mismatch(self):
        t = User_Score_Tracker(0, 0.5)
        t.add(1)

        assert t.n_seen == 1
        assert t.n_matched == 0
        assert t.current() == 0

    def test_0_add_match(self):
        t = User_Score_Tracker(0, 0.5)
        t.add(0)

        assert t.n_seen == 1
        assert t.n_matched == 1
        assert t.current() == 1

    def test_1_add_many(self):
        t = User_Score_Tracker(1, 0.5)
        annotations = [1, 0, 1, 0, 1, 0, 1, 0]
        for i in annotations:
            t.add(i)

        # +1 because epsilon gets added to the history
        assert len(t._history) == len(annotations) + 1
        assert t.calculateScore() == .5


class Test_Labeled_Trackers:

    def test_init_User_Tracker(self):
        tracker = User_Score_Tracker
        labels = [0, 1, 2]
        value = .5
        l = Labeled_Trackers(tracker, labels, value)

        for i in labels:
            assert type(l.trackers[i]) is tracker
            assert l.trackers[i].current() == value

        assert len(l.trackers) == 3

    def test_add_tracker(self):
        l = Labeled_Trackers(User_Score_Tracker, [0, 1])
        l.add(User_Score_Tracker, 2, .5)

        assert len(l.trackers) == 3
        assert l.trackers[2].label == 2

    def test_getAll(self):
        tracker = User_Score_Tracker
        labels = [0, 1, 2]
        value = .5
        l = Labeled_Trackers(tracker, labels, value)

        assert l.getAll() == l.trackers



