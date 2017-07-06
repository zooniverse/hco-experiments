
import swap.app.control as control
import swap.app.caesar_app as app
import swap.agents.subject
from swap.db import DB
from swap.utils.classification import Classification
from swap.utils.golds import GoldGetter

import json
import os

from unittest.mock import MagicMock, patch

# pylint: disable=R0201

path = os.path.dirname(__file__)
path = os.path.join(path, 'mock_request.json')
with open(path, 'r') as file:
    _json = json.load(file)


class TestCaesarApp:
    mock_classification = _json

    @patch.object(control.OnlineControl, 'run')
    @patch.object(GoldGetter, 'golds', {})
    @patch('swap.config.back_update', False)
    @patch('swap.config.database.name', 'swapDBtest')
    @patch('swap.config.database.builder.annotation.true', [1])
    @patch('swap.config.database.builder.annotation.false', [0])
    def test_parse_annotation(self, run):
        oc = control.OnlineControl()
        cl = oc.parse_classification(self.mock_classification)
        print(cl)

        assert cl.user == 1437100
        assert cl.subject == 10532146
        assert cl.annotation == 1


    @patch.object(control.OnlineControl, 'run')
    @patch.object(GoldGetter, 'golds', {})
    @patch('swap.config.back_update', False)
    @patch('swap.config.database.name', 'swapDBtest')
    def test_classify(self, run):
        DB._reset()
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(Classification(0, 1, 1))

        assert isinstance(ret, swap.agents.subject.Subject)
        assert ret.score == 0.12

    def test_generate_address(self):
        assert app.generate_address() == \
            'http://localhost:3000/workflows/1737/reducers/swap/reductions'
