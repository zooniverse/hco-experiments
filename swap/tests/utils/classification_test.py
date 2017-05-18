
import pytest

from swap.utils.classification import Classification, ClValueError


class Test_Classification:
    def test_classification_gold_init(self):
        cl = Classification(0, 0, 0)

        print(cl)
        print(cl.gold_label)
        assert cl.isgold() is False
        assert cl.gold is False

    def test_init_type_errors(self):
        with pytest.raises(ClValueError):
            Classification(1, 1, '1')
