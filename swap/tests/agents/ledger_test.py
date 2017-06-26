################################################################
# pylint: disable=R0201

from swap.agents.ledger import Ledger, Transaction, StaleException
from swap.agents.subject import Ledger as SLedger
from swap.agents.subject import Transaction as STransaction
from swap.agents.user import User
from swap.agents.user import Ledger as ULedger
from swap.agents.user import Transaction as UTransaction
from swap.agents.user import Counter
from swap.agents.bureau import Bureau

import swap.config as config

from unittest.mock import MagicMock, patch

import pytest


def mocksubject(i=0, g=-1):
    s = MagicMock()
    s.id = i
    s.gold = g
    s.score = 0.12

    return s


def mockuser(i=0, score=(0.5, 0.5)):
    u = MagicMock()
    u.id = i
    u.score = score

    return u


class TestLedger:
    def test_init(self):
        le = Ledger(15)
        assert le.id == 15
        assert le.transactions == {}
        assert le.stale is True
        assert le.changed == []

    def test_add_transaction(self):
        le = Ledger(0)
        t0 = Transaction(mocksubject(0), 0)
        t1 = Transaction(mocksubject(1), 0)

        le.add(t0)
        le.add(t1)

        assert le.transactions[0] == t0
        assert le.transactions[1] == t1

        assert t0.order == 0
        assert t1.order == 1

    def test_add_registers_change(self):
        le = Ledger(0)
        t0 = Transaction(mocksubject(0), 0)
        t1 = Transaction(mocksubject(1), 0)

        le.add(t0)
        le.add(t1)

        assert 0 in le.changed
        assert 1 in le.changed
        assert le.stale is True

    def test_get(self):
        le = Ledger(0)
        t = Transaction(mocksubject(0), 0)
        le.add(t)

        assert le.get(0) == t

    def test_update(self):
        le = Ledger(0)
        t0 = Transaction(mocksubject(0), 0)
        t0.notify = MagicMock()

        le.add(t0)
        le.update(0)

        t0.notify.assert_not_called

    def test_update_registers_change(self):
        le = Ledger(0)
        t0 = Transaction(mocksubject(0), 0)
        t1 = Transaction(mocksubject(1), 0)

        le.add(t0)
        le.add(t1)

        le.recalculate()
        le.update(0)

        assert le.changed == [0]
        assert le.stale is True

    def test_recalculate_clears_changes(self):
        le = Ledger(0)
        t0 = Transaction(mocksubject(0), 0)
        t1 = Transaction(mocksubject(1), 0)

        le.add(t0)
        le.add(t1)

        le.recalculate()

        assert le.changed == []
        assert le.stale is False

    def test_change(self):
        le = Ledger(0)
        le._change(1)

        assert 1 in le.changed

    # def test_missing_bureau(self):
    #     le = Ledger(0)

    #     with pytest.raises(MissingReference):
    #         le.restore_agent(15)

    @patch.object(Transaction, 'agent', return_value=MagicMock())
    def test_notify_agents_getsagent(self, mock):
        l = Ledger(0)
        [l.add(Transaction(mocksubject(i), 0)) for i in range(5)]
        l.notify_agents(None)

        assert mock.call_count == 5

    def test_notify_agents_callsnotify(self):
        subject = mocksubject(0)
        t = Transaction(mocksubject(1), 0)
        mock = MagicMock(return_value=subject)
        t.agent = mock

        l = Ledger(15)
        l.add(t)
        l.notify_agents(16)

        print(subject)
        subject.ledger.notify.assert_called_once_with(15, 16)


class TestTransaction:

    def test_init(self):
        t = Transaction(mocksubject(15), 20)
        assert t.id == 15
        assert t.annotation == 20
        assert t.order is None
        assert t.score is None
        assert t.change is None

    # def test_delref(self):
    #     t = Transaction(0, User(0))
    #     t.delref()

    #     assert t._agent is None

    # def test_restore(self):
    #     t = Transaction(mocksubject(0), 0)
    #     u = User(0)
    #     t.restore(u)

    #     assert t._agent == u

    # def test_notify(self):
    #     mock = MagicMock()
    #     t = Transaction(mock)
    #     t.notify(100)

    #     mock.ledger.update.assert_called_once_with(100)

    # def test_set_restore_callback(self):
    #     t = Transaction(mocksubject(0), 0)
    #     mock = MagicMock()
    #     t.set_restore_callback(mock)
    #     t.restore_callback()

    #     mock.assert_called_once_with()

    def test_builtins(self):
        t = Transaction(mocksubject(1), 0)
        print(t)

    # def test_agent_missing(self):
    #     t = Transaction(mocksubject(1), 0)

    #     with pytest.raises(MissingReference):
    #         t.agent

    # def test_agent_missing_callback(self):
    #     t = Transaction(mocksubject(1), 0)
    #     mock = MagicMock()
    #     t.set_restore_callback(mock)

    #     t.agent
    #     mock.assert_called_once_with()


class TestSubjectLedger:
    def test_init(self):
        le = SLedger(16)
        assert le.id == 16
        assert le.last is None
        assert le._score is None
        assert le.first_change is None

    @patch.object(SLedger, 'recalculate', MagicMock())
    def test_score_stale(self):
        le = SLedger(0)
        le.stale = True

        with pytest.raises(StaleException):
            le.score

    def test_add_transaction_last(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)

        le.add(t0)
        le.add(t1)

        assert le.last == t1

    def test_add_transaction_links(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)

        le.add(t0)
        le.add(t1)

        assert t1.left == t0
        assert t0.right == t1

        assert t1.right is None
        assert t0.left is None

    @patch.object(STransaction, 'calculate', MagicMock(return_value=.5))
    def test_update_first_change(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)
        t2 = STransaction(mockuser(2), 0)

        t1.notify = MagicMock()

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.clear_changes()
        le.update(1)

        print(le.changed)
        assert le.first_change == t1

    def test_change(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)

        le.add(t0)
        le.add(t1)
        le.clear_changes()

        le._change(0)
        assert le.first_change == t0

    @patch.object(STransaction, 'calculate', new=MagicMock(return_value=.5))
    @patch.object(STransaction, 'get_prior', new=MagicMock(return_value=.5))
    def test_recalculate_beginning(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)
        t2 = STransaction(mockuser(2), 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.recalculate()
        assert STransaction.calculate.call_count == 3

    @patch.object(STransaction, 'calculate', new=MagicMock(return_value=.5))
    @patch.object(STransaction, 'get_prior', new=MagicMock(return_value=.5))
    def test_recalculate_middle(self):
        le = SLedger(0)
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(1), 0)
        t2 = STransaction(mockuser(2), 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.changed = [1]
        le.recalculate()
        assert STransaction.calculate.call_count == 2

    def test_recalculate_real(self):
        def u(i):
            return mockuser(i, score=(.25, .25))
        le = SLedger(0)
        for x in range(10):
            le.add(STransaction(u(x), 0))

        score = le.recalculate()
        print(score)
        assert score - 0.9998785824 < 1e-6

    def test_recalculate_empty(self):
        le = SLedger(0)
        assert le.recalculate() == 0.12

    def test_recalculate_propagates(self):
        def u(i, s):
            return mockuser(i, s)

        le = SLedger(0)
        t0 = STransaction(u(0, (3 / 4, 3 / 4)), 1)
        t1 = STransaction(u(1, (1 / 4, 1 / 4)), 1)

        le.add(t0)
        le.add(t1)

        le.recalculate()

        assert le.score - .12 < 1e-10

    @patch('swap.config.back_update', False)
    @patch.object(STransaction, 'calculate')
    def test_add_legacy_callscalculate(self, mock):
        le = SLedger(0)
        t = STransaction(mockuser(0), 0)
        le.add(t)

        mock.assert_called_once_with()

    @patch('swap.config.back_update', True)
    @patch.object(STransaction, 'calculate')
    def test_add_legacy_nocalculate(self, mock):
        le = SLedger(0)
        t = STransaction(mockuser(0), 0)
        le.add(t)

        assert mock.call_count == 0


class TestSubjectTransaction:
    def test_init(self):
        t = STransaction(mockuser(0), 0)

        assert t.id == 0
        assert t.user_score == (0.5, 0.5)
        assert t.change == (0.5, 0.5)
        assert t.annotation == 0
        assert t.score is None

        assert t.left is None
        assert t.right is None

    def test_get_prior_first(self):
        t = STransaction(mocksubject(0), 0)

        assert t.get_prior() == 0.12

    def test_get_prior_middle(self):
        user = MagicMock()
        t0 = STransaction(mockuser(0), 0)
        t1 = STransaction(mockuser(0), 0)

        t1.left = t0
        t0.score = 15

        assert t1.get_prior() == 15

    def test_notify(self):
        t = STransaction(mockuser(1), 0)
        t.notify(mockuser(15, (0.1, 0.9)))

        assert t.change == (0.1, 0.9)
        assert t.user_score == (0.5, 0.5)

    def test_commit_change(self):
        t = STransaction(mockuser(1), 0)
        t.notify(mockuser(15, (0.1, 0.9)))
        t.commit_change()

        assert t.change == (0.1, 0.9)
        assert t.user_score == (0.1, 0.9)

    def test_calculate_nocommit(self):
        t = STransaction(mockuser(1), 0)
        t.notify(mockuser(15, (0.1, 0.9)))

        assert t.calculate(.12) == .12

    def test_calculate_1(self):
        user = mockuser(0, (.25, .8))

        t = STransaction(user, 1)
        assert t.calculate(.12) - .096 / .756 < 1e-10

    def test_calculate_0(self):
        t = STransaction(mockuser(0, (.25, .8)), 0)
        assert t.calculate(.12) - .024 / .244 < 1e-10


class TestUserLedger:

    def test_init(self):
        le = ULedger(17)
        assert le.id == 17
        assert type(le.no) is Counter
        assert type(le.yes) is Counter
        assert le._score == (0.5, 0.5)

    def test_add(self):
        le = ULedger(0)
        t = UTransaction(mocksubject(0), 0)
        le.add(t)
        assert t.gold is None

    @patch('swap.config.back_update', False)
    @patch.object(ULedger, 'recalculate')
    def test_add_legacyrecalculate(self, mock):
        le = ULedger(0)
        mock.reset_mock()

        t = UTransaction(mocksubject(0), 0)
        le.add(t)

        le.recalculate.assert_called_once_with()

    @patch('swap.config.back_update', True)
    @patch.object(ULedger, 'recalculate')
    def test_add_backupdaterecalculate(self, mock):
        le = ULedger(0)
        mock.reset_mock()
        t = UTransaction(mocksubject(0), 0)
        le.add(t)

        assert mock.call_count == 0

    def test_recalculate_1(self):
        le = ULedger(0)
        t0 = UTransaction(mocksubject(0, 0), 0)
        t1 = UTransaction(mocksubject(1, 1), 0)
        t2 = UTransaction(mocksubject(2, 1), 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        assert le.recalculate() == (2 / 3, 1 / 4)

    def test_recalculate_2(self):
        le = ULedger(0)
        t0 = UTransaction(mocksubject(0, 1), 0)
        t1 = UTransaction(mocksubject(1, 1), 0)
        t2 = UTransaction(mocksubject(2, 1), 0)
        t3 = UTransaction(mocksubject(2, 1), 1)

        le.add(t0)
        le.add(t1)
        le.add(t2)
        le.add(t3)

        assert le.recalculate() == (1 / 2, 2 / 5)

    def test_score(self):
        le = ULedger(0)
        t0 = UTransaction(mocksubject(0, 1), 0)
        t1 = UTransaction(mocksubject(1, 1), 0)
        t2 = UTransaction(mocksubject(2, 1), 0)
        t3 = UTransaction(mocksubject(2, 1), 1)

        le.add(t0)
        le.add(t1)
        le.add(t2)
        le.add(t3)

        le.recalculate()

        assert le.score == (1 / 2, 2 / 5)

    def test_no_gold(self):
        le = ULedger(0)
        for i in range(0):
            t = UTransaction(mocksubject(-1), 0)
            le.add(t)

        assert le.recalculate() == (0.5, 0.5)

    # def test_calculate(self):
    #     le = ULedger(0)
    #     le.no = 5
    #     le.yes = 6
    #     le.transactions = [0 for i in range(10)]

    #     assert le._calculate()[0] == 6 / 12
    #     assert le._calculate()[1] == 7 / 12

    # def test_recalculate(self):
    #     le = ULedger(0)
    #     t0 = UTransaction(0, )


class TestUserTransaction:
    def test_init(self):
        t = UTransaction(mocksubject(0, 0), 0)
        assert t.annotation == 0
        assert t.gold is None
        assert t.change == 0

    def test_notify(self):
        t = UTransaction(mocksubject(1, 1), 0)
        t.notify(mocksubject(1, 1))

        assert t.change == 1
        assert t.gold is None

    def test_commit_change(self):
        t = UTransaction(mocksubject(1, 1), 0)
        t.notify(mocksubject(1, 1))
        t.commit_change()

        assert t.change == 1
        assert t.gold == 1

    def test_changed(self):
        t = UTransaction(mocksubject(1, 1), 0)
        t.notify(mocksubject(1, 1))

        assert t.changed

    def test_unchanged(self):
        t = UTransaction(mocksubject(1, 1), 0)
        t.notify(mocksubject(1, 1))
        t.commit_change()

        assert not t.changed

    def test_matched(self):
        t = UTransaction(mocksubject(0, 0), 0)
        t.commit_change()

        assert t.matched

    def test_unmatched(self):
        t = UTransaction(mocksubject(0, 0), 1)
        t.commit_change()

        assert not t.matched


class TestUserCounter:
    def test_init(self):
        c = Counter()
        assert c.seen == 0
        assert c.matched == 0

    def test_see(self):
        c = Counter()
        c.see()
        assert c.seen == 1
        assert c.matched == 0

    def test_unsee(self):
        c = Counter()
        c.seen = 5
        c.matched = 5
        c.unsee()
        assert c.seen == 4
        assert c.matched == 5

    def test_match(self):
        c = Counter()
        c.match()
        assert c.matched == 1
        assert c.seen == 1

    def test_unmatch(self):
        c = Counter()
        c.seen = 5
        c.matched = 5
        c.unmatch()
        assert c.seen == 4
        assert c.matched == 4


# class TestDynamicReferencing:

#     def test_nuke(self):
#         le = Ledger(15)
#         mock = MagicMock()
#         t = Transaction(mock)

#         le.add(t)
#         le.nuke()

#         mock.ledger.delrefs.assert_called_once_with(15)

#     def test_delrefs(self):
#         le = Ledger(15)
#         t = Transaction(16, mocksubject())
#         t.delref = MagicMock()
#         le.add(t)

#         le.delrefs(16)
#         t.delref.assert_called_once_with()

#     def test_delete_all_agents(self):

#         le = Ledger(0)
#         u = User(0)
#         for i in range(5):
#             le.add(Transaction(i, u))

#         le.delete_all_agents()

#         for t in le:
#             assert t._agent is None

#     def test_transaction_restore(self):
#         le = Ledger(0)
#         bureau = Bureau(User)
#         le.set_bureau(bureau)
#         user = bureau.get(15)

#         t = Transaction(15, mocksubject())
#         le.add(t)

#         assert t.agent == user

#     def test_transaction_restore2(self):
#         le = Ledger(0)
#         bureau = Bureau(User)
#         le.set_bureau(bureau)
#         user = bureau.get(15)

#         t = Transaction(15, mocksubject())
#         le.add(t)
#         t.restore_callback = None
#         t.set_restore_callback(lambda: le.restore_agent(t.id))

#         assert t.agent == user
