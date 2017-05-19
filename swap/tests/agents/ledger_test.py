################################################################

from swap.agents.ledger import Ledger, Transaction
from swap.agents.subject import Ledger as SLedger
from swap.agents.subject import Transaction as STransaction
from swap.agents.user import User
from swap.agents.user import Ledger as ULedger
from swap.agents.user import Transaction as UTransaction
from swap.agents.user import Counter

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
        le.change(1)

        assert 1 in le.changed


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

        le.change(0)
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
