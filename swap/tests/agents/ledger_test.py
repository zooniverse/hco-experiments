################################################################

from swap.agents.ledger import Ledger, Transaction, MissingReference
from swap.agents.subject import Ledger as SLedger
from swap.agents.subject import Transaction as STransaction
from swap.agents.user import User
from swap.agents.user import Ledger as ULedger
from swap.agents.user import Transaction as UTransaction
from swap.agents.user import Counter
from swap.agents.bureau import Bureau

from unittest.mock import MagicMock, patch

import pytest


class TestLedger:
    def test_init(self):
        le = Ledger(15)
        assert le.id == 15
        assert le.transactions == {}
        assert le.stale is True
        assert le.changed == []

    def test_add_transaction(self):
        le = Ledger(0)
        t0 = Transaction(0, None)
        t1 = Transaction(1, None)

        le.add(t0)
        le.add(t1)

        assert le.transactions[0] == t0
        assert le.transactions[1] == t1

        assert t0.order == 0
        assert t1.order == 1

    def test_add_registers_change(self):
        le = Ledger(0)
        t0 = Transaction(0, None)
        t1 = Transaction(1, None)

        le.add(t0)
        le.add(t1)

        assert 0 in le.changed
        assert 1 in le.changed
        assert le.stale is True

    def test_get(self):
        le = Ledger(0)
        t = Transaction(0, None)
        le.add(t)

        assert le.get(0) == t

    def test_update(self):
        le = Ledger(0)
        t0 = Transaction(0, None)
        t0.notify = MagicMock()

        le.add(t0)
        le.update(0)

        t0.notify.assert_not_called

    def test_update_registers_change(self):
        le = Ledger(0)
        t0 = Transaction(0, None)
        t1 = Transaction(1, None)

        le.add(t0)
        le.add(t1)

        le.recalculate()
        le.update(0)

        assert le.changed == [0]
        assert le.stale is True

    def test_recalculate_clears_changes(self):
        le = Ledger(0)
        t0 = Transaction(0, None)
        t1 = Transaction(1, None)

        le.add(t0)
        le.add(t1)

        le.recalculate()

        assert le.changed == []
        assert le.stale is False

    def test_change(self):
        le = Ledger(0)
        le._change(1)

        assert 1 in le.changed

    def test_missing_bureau(self):
        le = Ledger(0)

        with pytest.raises(MissingReference):
            le.restore_agent(15)


class TestTransaction:

    def test_init(self):
        t = Transaction(1, 2)
        assert t.id == 1
        assert t._agent == 2
        assert t.order is None
        assert t.restore_callback is None

    def test_delref(self):
        t = Transaction(0, User(0))
        t.delref()

        assert t._agent is None

    def test_restore(self):
        t = Transaction(0, None)
        u = User(0)
        t.restore(u)

        assert t._agent == u

    def test_notify(self):
        mock = MagicMock()
        t = Transaction(0, mock)
        t.notify(100)

        mock.ledger.update.assert_called_once_with(100)

    def test_set_restore_callback(self):
        t = Transaction(0, None)
        mock = MagicMock()
        t.set_restore_callback(mock)
        t.restore_callback()

        mock.assert_called_once_with()

    def test_builtins(self):
        t = Transaction(1, None)
        print(t)

    def test_agent_missing(self):
        t = Transaction(1, None)

        with pytest.raises(MissingReference):
            t.agent

    def test_agent_missing_callback(self):
        t = Transaction(1, None)
        mock = MagicMock()
        t.set_restore_callback(mock)

        t.agent
        mock.assert_called_once_with()


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
        le.score

        le.recalculate.asert_called_once()

    def test_add_transaction_last(self):
        le = SLedger(0)
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)

        le.add(t0)
        le.add(t1)

        assert le.last == t1

    def test_add_transaction_links(self):
        le = SLedger(0)
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)

        le.add(t0)
        le.add(t1)

        assert t1.left == t0
        assert t0.right == t1

        assert t1.right is None
        assert t0.left is None

    @patch.object(STransaction, 'calculate', MagicMock(return_value=.5))
    def test_update_first_change(self):
        le = SLedger(0)
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)
        t2 = STransaction(2, None, 0)

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
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)

        le.add(t0)
        le.add(t1)
        le.clear_changes()

        le._change(0)
        assert le.first_change == t0

    @patch.object(STransaction, 'calculate', new=MagicMock(return_value=.5))
    @patch.object(STransaction, 'get_prior', new=MagicMock(return_value=.5))
    def test_recalculate_beginning(self):
        le = SLedger(0)
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)
        t2 = STransaction(2, None, 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.recalculate()
        assert STransaction.calculate.call_count == 3

    @patch.object(STransaction, 'calculate', new=MagicMock(return_value=.5))
    @patch.object(STransaction, 'get_prior', new=MagicMock(return_value=.5))
    def test_recalculate_middle(self):
        le = SLedger(0)
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)
        t2 = STransaction(2, None, 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.changed = [1]
        le.recalculate()
        assert STransaction.calculate.call_count == 2

    def test_recalculate_real(self):
        def u(i):
            user = MagicMock()
            user.score = (.25, .25)
            return user
        le = SLedger(0)
        for x in range(10):
            le.add(STransaction(x, u(x), 0))

        score = le.recalculate()
        print(score)
        assert False

    def test_recalculate_empty(self):
        le = SLedger(0)
        assert le.recalculate() == 0.12

    def test_recalculate_propagates(self):
        def user(a, b):
            u = MagicMock()
            u.score = (a, b)
            return u

        le = SLedger(0)
        t0 = STransaction(0, user(3 / 4, 3 / 4), 1)
        t1 = STransaction(1, user(1 / 4, 1 / 4), 1)

        le.add(t0)
        le.add(t1)

        assert le.score - .12 < 1e-10


class TestSubjectTransaction:
    def test_init(self):
        user = MagicMock()
        t = STransaction(0, user, 0)

        assert t.id == 0
        assert t.agent == user
        assert t.annotation == 0
        assert t.score is None

        assert t.left is None
        assert t.right is None

    def test_get_prior_first(self):
        user = MagicMock()
        t = STransaction(0, user, 0)

        assert t.get_prior() == 0.12

    def test_get_prior_middle(self):
        user = MagicMock()
        t0 = STransaction(0, user, 0)
        t1 = STransaction(0, user, 0)

        t1.left = t0
        t0.score = 15

        assert t1.get_prior() == 15

    def test_notify(self):
        user = MagicMock()
        t = STransaction(15, user, 0)
        t.notify(25)
        user.ledger.update.assert_called_once_with(25)

    def test_calculate_1(self):
        user = MagicMock()
        user.score = (.25, .8)

        print(user.getScore(0))
        print(user.getScore(1))

        t = STransaction(0, user, 1)
        assert t.calculate(.12) - .096 / .756 < 1e-10

    def test_calculate_0(self):
        user = MagicMock()
        user.score = (.25, .8)
        print(*user.score)

        t = STransaction(0, user, 0)
        assert t.calculate(.12) - .024 / .244 < 1e-10


class TestUserLedger:
    def get_subject(self, gold):
        subject = MagicMock()
        subject.gold = gold
        return subject

    def test_init(self):
        le = ULedger(17)
        assert le.id == 17
        assert type(le.no) is Counter
        assert type(le.yes) is Counter
        assert le._score is None

    def test_add(self):
        subject = self.get_subject(0)

        le = ULedger(0)
        t = UTransaction(0, subject, 0)
        le.add(t)
        assert t.gold is None

    def test_recalculate_1(self):
        le = ULedger(0)
        t0 = UTransaction(0, self.get_subject(0), 0)
        t1 = UTransaction(1, self.get_subject(1), 0)
        t2 = UTransaction(2, self.get_subject(1), 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        assert le.recalculate() == (2 / 3, 1 / 4)

    def test_recalculate_2(self):
        le = ULedger(0)
        t0 = UTransaction(0, self.get_subject(1), 0)
        t1 = UTransaction(1, self.get_subject(1), 0)
        t2 = UTransaction(2, self.get_subject(1), 0)
        t3 = UTransaction(2, self.get_subject(1), 1)

        le.add(t0)
        le.add(t1)
        le.add(t2)
        le.add(t3)

        assert le.recalculate() == (1 / 2, 2 / 5)

    def test_score(self):
        le = ULedger(0)
        t0 = UTransaction(0, self.get_subject(1), 0)
        t1 = UTransaction(1, self.get_subject(1), 0)
        t2 = UTransaction(2, self.get_subject(1), 0)
        t3 = UTransaction(2, self.get_subject(1), 1)

        le.add(t0)
        le.add(t1)
        le.add(t2)
        le.add(t3)

        assert le.score == (1 / 2, 2 / 5)

    def test_notify(self):
        le = ULedger(0)
        t = UTransaction(0, self.get_subject(1), 0)

        le.notify_agents = MagicMock()
        le.score = 0.5
        le.notify_agents.assert_called_once_with()

    def test_no_gold(self):
        le = ULedger(0)
        s = MagicMock()
        s.gold = -1
        for i in range(0):
            t = UTransaction(i, s, 0)
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
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(0, subject, 0)

        assert t.agent == subject
        assert t.annotation == 0
        assert t.gold == 0

    def test_notify(self):
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(22, subject, 0)
        t.notify(23)
        t.agent.ledger.update.assert_called_once_with(23)

    def test_changed(self):
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(0, subject, 0)
        subject.gold = 1

        assert t.changed

    def test_unchanged(self):
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(0, subject, 0)

        assert not t.changed

    def test_matched(self):
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(0, subject, 0)

        assert t.matched

    def test_unmatched(self):
        subject = MagicMock()
        subject.gold = 0

        t = UTransaction(0, subject, 1)

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


class TestDynamicReferencing:

    def test_nuke(self):
        le = Ledger(15)
        mock = MagicMock()
        t = Transaction(1, mock)

        le.add(t)
        le.nuke()

        mock.ledger.delrefs.assert_called_once_with(15)

    def test_delrefs(self):
        le = Ledger(15)
        t = Transaction(16, None)
        t.delref = MagicMock()
        le.add(t)

        le.delrefs(16)
        t.delref.assert_called_once_with()

    def test_delete_all_agents(self):

        le = Ledger(0)
        u = User(0)
        for i in range(5):
            le.add(Transaction(i, u))

        le.delete_all_agents()

        for t in le:
            assert t._agent is None

    def test_transaction_restore(self):
        le = Ledger(0)
        bureau = Bureau(User)
        le.set_bureau(bureau)
        user = bureau.get(15)

        t = Transaction(15, None)
        le.add(t)

        assert t.agent == user

    def test_transaction_restore2(self):
        le = Ledger(0)
        bureau = Bureau(User)
        le.set_bureau(bureau)
        user = bureau.get(15)

        t = Transaction(15, None)
        le.add(t)
        t.restore_callback = None
        t.set_restore_callback(lambda: le.restore_agent(t.id))

        assert t.agent == user
