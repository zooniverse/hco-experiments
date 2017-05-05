################################################################
# Test functions for tracker classes

from swap.agents.tracker import *
from swap.agents.user import User_Score_Tracker

import pytest


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

        assert t.calculateScore() == 41 / 102

    def test_0_add_mismatch(self):
        t = User_Score_Tracker(0, 0.5)
        t.add(1)

        assert t.n_seen == 1
        assert t.n_matched == 0
        assert t.current() == 1 / 3

    def test_0_add_match(self):
        t = User_Score_Tracker(0, 0.5)
        t.add(0)

        assert t.n_seen == 1
        assert t.n_matched == 1
        assert t.current() == 2 / 3

    def test_1_add_many(self):
        t = User_Score_Tracker(1, 0.5)
        annotations = [1, 0, 1, 0, 1, 0, 1, 0]
        for i in annotations:
            t.add(i)

        # +1 because epsilon gets added to the history
        assert len(t._history) == len(annotations) + 1
        assert t.calculateScore() == .5


class TestTrackerCollection:

    def test_init_User_Tracker(self):
        tracker = User_Score_Tracker
        labels = [0, 1, 2]
        value = .5
        tc = Tracker_Collection.Generate(tracker, labels, value)

        for i in labels:
            assert type(tc.trackers[i]) is tracker
            assert tc.trackers[i].current() == value

        assert len(tc.trackers) == 3

    def test_add(self):
        tc = Tracker_Collection.Generate(User_Score_Tracker, [0, 1])
        tc.addNew(User_Score_Tracker, 2, .5)

        assert len(tc.trackers) == 3
        assert tc.trackers[2].label == 2

    def test_remove(self):
        t = Tracker()
        tc = Tracker_Collection()
        tc.add(1, t)
        tc.add(2, t)

        ret = tc.remove(2)
        assert 1 in tc.trackers
        assert 2 not in tc.trackers
        assert ret == t

    def test_getAll(self):
        tracker = User_Score_Tracker
        labels = [0, 1, 2]
        value = .5
        tc = Tracker_Collection.Generate(tracker, labels, value)

        assert tc.getAll() == tc.trackers

    def test_tracker_name_error(self):
        t = Tracker()
        tc = Tracker_Collection()
        tc.add(1, t)
        with pytest.raises(NameError):
            tc.add(1, t)

    def test_tracker_type_error(self):
        t = object()
        tc = Tracker_Collection()
        with pytest.raises(TypeError):
            tc.add(1, t)

    def test_generator_value_error(self):
        with pytest.raises(ValueError):
            Tracker_Collection.Generate(None, None)
