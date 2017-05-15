################################################################

from swap.agents.ledger import Ledger, Transaction
from swap.agents.subject import Ledger as SLedger
from swap.agents.subject import Transaction as STransaction

from unittest.mock import MagicMock, patch


class TestLedger:
    def test_init(self):
        le = Ledger()
        assert le.transactions == {}
        assert le.first_change is None
        assert le.last is None

    def test_add_transaction(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)

        le.add(t0)
        le.add(t1)

        assert le.transactions[0] == t0
        assert le.transactions[1] == t1

        assert t0.order == 0
        assert t1.order == 1

    def test_add_transaction_last(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)

        le.add(t0)
        le.add(t1)

        assert le.last == t1

    def test_add_transaction_links(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)

        le.add(t0)
        le.add(t1)

        assert t1.left == t0
        assert t0.right == t1

        assert t1.right is None
        assert t0.left is None

    def test_change(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)

        le.add(t0)
        le.add(t1)
        le.first_change = t1

        le._change(t0)
        assert le.first_change == t0

    def test_update(self):
        le = Ledger()
        t0 = Transaction(0)
        le.add(t0)

        def f(item):
            item.order = 55

        le.update(0, f)
        assert t0.order == 55

    def test_update_registers_change(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)
        t2 = Transaction(2)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.recalculate()
        le.update(1, lambda item: None)

        assert le.first_change == t1

    def test_recalculate_clears_changes(self):
        le = Ledger()
        t0 = Transaction(0)
        t1 = Transaction(1)
        t2 = Transaction(2)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.recalculate()
        assert le.first_change is None


# def my_patch(func, method, mock):
#     def wrapper(*args, **kwargs):
#         method = 


class TestSubjectLedger:

    @patch.object(STransaction, 'calculate', new=MagicMock(return_value=.5))
    @patch.object(STransaction, 'get_prior', new=MagicMock(return_value=.5))
    def test_recalculate_beginning(self):
        le = SLedger()
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
        le = SLedger()
        t0 = STransaction(0, None, 0)
        t1 = STransaction(1, None, 0)
        t2 = STransaction(2, None, 0)

        le.add(t0)
        le.add(t1)
        le.add(t2)

        le.first_change = t1
        le.recalculate()
        assert STransaction.calculate.call_count == 2


class TestSubjectTransaction:
    def test_init(self):
        user = MagicMock()
        t = STransaction(0, user, 0)

        assert t.id == 0
        assert t.user == user
        assert t.annotation == 0
        assert t.score is None

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

    def test_calculate_1(self):
        user = MagicMock()

        def get_score(n):
            if n == 0:
                return .25
            elif n == 1:
                return .80
        user.getScore = get_score

        print(user.getScore(0))
        print(user.getScore(1))

        t = STransaction(0, user, 1)
        assert t.calculate(.12) - .096 / .756 < 1e-10

    def test_calculate_0(self):
        user = MagicMock()

        def get_score(n):
            if n == 0:
                return .25
            elif n == 1:
                return .80
        user.getScore = get_score

        print(user.getScore(0))
        print(user.getScore(1))

        t = STransaction(0, user, 0)
        assert t.calculate(.12) - .024 / .244 < 1e-10
