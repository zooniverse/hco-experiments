################################################################
# Test functions for bootstrap metrics

from unittest.mock import MagicMock
from bootstrap import Bootstrap
from bootstrap.analysis import Metric
from swap.swap import SWAP
from swap.db import classifications as dbcl


class Mock_Bootstrap(Bootstrap):
    def __init__(self):
        silver = {}
        for i in range(50):
            silver[i] = 0
        for i in range(50, 102):
            silver[i] = 1
        self.silver = silver

        self.t_low = 501
        self.t_high = 503

        self.bureau = MagicMock()
        self.metrics = MagicMock()

        self.p0 = .12
        self.epsilon = .5

        self.n = 3


class Mock_Swap(SWAP):
    mock_stats = MagicMock()

    def __init__(self):
        pass

    @property
    def stats(self):
        self.mock_stats


class Test_Metric:

    def test_init(self):
        boot = Mock_Bootstrap()
        swap = Mock_Swap()

        metric = Metric(boot, swap, 5)

        assert metric.num == 5
        assert metric.silver == boot.silver
        assert metric.iteration == 3
        assert metric.stats == swap.stats

        assert metric.thresholds == (boot.t_low, boot.t_high)

    def test_num_silver(self):
        boot = Mock_Bootstrap()
        swap = Mock_Swap()

        mock = MagicMock(return_value=102)
        dbcl.getNSubjects = mock
        dbcl.getExpertGold = MagicMock()

        metric = Metric(boot, swap, 5)

        count = metric.num_silver()

        assert count[0] == 50
        assert count[1] == 52
        assert count[2] == 0

    def test_silver_accuracy(self):
        boot = Mock_Bootstrap()
        swap = Mock_Swap()

        mock_experts = {}
        for i in range(0, 25):
            mock_experts[i] = 0
        for i in range(25, 50):
            mock_experts[i] = 1
        for i in range(50, 75):
            mock_experts[i] = 0
        for i in range(75, 100):
            mock_experts[i] = 1
        mock = MagicMock(return_value=mock_experts)
        dbcl.getExpertGold = mock

        metric = Metric(boot, swap, 5)
        accuracy = metric.silver_accuracy()

        assert accuracy.stats[0] == (25, 50)
        assert accuracy.stats[1] == (25, 50)
        assert accuracy.total() == (50, 100)
