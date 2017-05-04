################################################################
# Test functions for stats classes

from swap.agents.agent import Stat
from swap.agents.agent import MultiStat
# from swap.agents.agent import Stats
from swap.agents.agent import Accuracy
import statistics

import unittest


class Test_Stat:
    data = [0, 0, 0, 0, 1, 1, 1, 1]

    def test_mean(self):
        s = Stat(self.data)
        print(s)
        assert s.mean == .5

    def test_median(self):
        s = Stat(self.data)
        print(s)
        assert s.median == 0.5

        s = Stat(self.data + [1])
        print(s)
        assert s.median == 1

    def test_stdev(self):
        s = Stat(self.data)
        print(s)
        assert s.stdev == statistics.pstdev(self.data)

    def test_export(self):
        s = Stat(self.data)
        print(s)
        export = s.export()
        assert 'mean' in export
        assert 'median' in export
        assert 'stdev' in export


class Test_Multistat:
    data1 = [0, 0, 0, 0, 1, 1, 1, 1]
    data2 = [0, 0, 0, 0, 0, 0, 1, 1]

    def test_export(self):
        m = MultiStat((1, self.data1), (2, self.data2))

        export = m.export()
        print(export)
        assert 1 in export
        assert 2 in export

        assert export[1] == Stat(self.data1).export()
        assert export[2] == Stat(self.data2).export()

    def test_add_new(self):
        m = MultiStat()
        m.addNew(1, self.data1)

        assert m.export()[1] == Stat(self.data1).export()

    def test_add(self):
        m = MultiStat()
        m.addNew(1, self.data1)

        assert 1 in m.export()


class Test_Accuracy(unittest.TestCase):

    def test_add(self):
        a = Accuracy()
        a.add(0, 1, 10)

        assert 0 in a.stats
        assert a.stats[0] == (1, 10)

    def test_add_invalid(self):
        a = Accuracy()
        with self.assertRaises(ValueError):
            a.add(0, 10, 1)

    def test_score(self):
        a = Accuracy()
        assert a.score(1, 10) == .1

    def test_score_0(self):
        a = Accuracy()
        assert a.score(10, 0) == 0
