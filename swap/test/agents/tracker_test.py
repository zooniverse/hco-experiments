################################################################
# Test functions for tracker classes

from swap.agents.tracker import *


class Test_Tracker:
    def test_init(self):
        t = Tracker()

        assert type(t.history) is list
        assert t.current is None
        assert t.n == 0

    def test_init_value(self):
        t = Tracker(.5)

        assert type(t.history) is list
        assert t.history == [.5]
        assert t.current is .5
        assert t.n == 1

    def test_add(self):
        t = Tracker()
        t.add(.5)

        assert t.history == [.5]
        assert t.current == .5
        assert t.n == 1

    def test_add_many(self):
        t = Tracker()
        items = [1, 2, 3, 4, 5]
        for i in items:
            t.add(i)

        assert t.history == items
        assert t.current == 5
        assert t.n == 5

    def test_get_current(self):
        t = Tracker()
        items = [5, 4, 3, 2, 1]
        for i in items:
            t.add(i)

        assert t.getCurrent() == 1

