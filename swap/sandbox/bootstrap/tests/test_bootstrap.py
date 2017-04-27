################################################################
# Test functions for bootstrap metrics

from unittest.mock import MagicMock
from bootstrap import Bootstrap
from bootstrap import BootstrapControl
from swap.db import classifications as dbcl
from swap.swap import Classification


class Test_Bootstrap:
    default_args = (.01, .99, .12, .5)
    def test_init(self):
        dbcl.getExpertGold = MagicMock(return_value={})
        b = Bootstrap(1, 2, 3, 4)

        assert b.golds == {}
        assert b.silver == {}
        assert b.t_low == 1
        assert b.t_high == 2
        assert b.p0 == 3
        assert b.epsilon == 4

    def test_set_threshold(self):
        b = Bootstrap(*self.default_args)
        b.setThreshold(1, 2)
        assert b.t_low == 1
        assert b.t_high == 2


class Test_Bootstrap_Control:
    def test_delegate_gold(self):
        cl = Classification('user', 'subject', 0, 0)
        dbcl.getAllGolds = MagicMock(return_value={})

        bc = BootstrapControl(.12, .5, {})
        mock = MagicMock()
        bc.swap = mock
        bc._delegate(cl)

        mock.processOneClassification.assert_called_with(
            cl, user=True, subject=False)

    def test_delegate_not_gold(self):
        cl = Classification('user', 'subject', 0)
        dbcl.getAllGolds = MagicMock(return_value={})

        bc = BootstrapControl(.12, .5, {})
        mock = MagicMock()
        bc.swap = mock
        bc._delegate(cl)

        mock.processOneClassification.assert_called_with(
            cl, user=False, subject=True)

