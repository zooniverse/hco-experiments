
import swap.app.control as control
from swap.utils.classification import Classification
from swap.utils.golds import GoldGetter
import json

from unittest.mock import MagicMock, patch


with open('mock_request.json', 'r') as file:
    _json = json.load(file)


class TestCaesarApp:
    mock_classification = _json

    def test_parse_annotation(self):
        cl = control.parse_classification(self.mock_classification)
        print(cl)

        assert cl.user == 1437100
        assert cl.subject == 10532146
        assert cl.annotation == 1


    @patch.object(control.OnlineControl, 'run')
    @patch.object(GoldGetter, 'golds', return_value=[])
    def test_classify(self, run, golds):
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(Classification(0, 1, 1))
        assert ret == 0.12
