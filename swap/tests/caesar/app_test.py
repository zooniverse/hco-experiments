
import swap.caesar.control as control
import swap.caesar.app as app
from swap.caesar.utils.address import Address
from swap.caesar.utils.requests import Requests
import swap.agents.subject
from swap.db import DB
from swap.db.db import Collection
from swap.db.classifications import Classifications
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
    @patch('swap.config.parser.annotation.task', 'T1')
    @patch('swap.config.parser.annotation.true', [1])
    @patch('swap.config.parser.annotation.false', [0])
    def test_parse_annotation(self, run):
        print(self.mock_classification)
        oc = control.OnlineControl()
        cl = oc.parse_raw(self.mock_classification)
        cl = oc.gen_cl(cl)
        print(cl)

        assert cl.user == 1437100
        assert cl.subject == 10532146
        assert cl.annotation == 1


    @patch.object(control.OnlineControl, 'run')
    @patch.object(GoldGetter, 'golds', {})
    @patch.object(Classifications, 'insert', MagicMock())
    @patch.object(Classifications, 'exists', MagicMock(return_value=False))
    @patch('swap.config.back_update', False)
    @patch('swap.config.database.name', 'swapDBtest')
    @patch('swap.config.parser.annotation.task', 'T1')
    @patch('swap.config.parser.annotation.true', [1])
    @patch('swap.config.parser.annotation.false', [0])
    def test_classify(self, run):
        DB._reset()
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(self.mock_classification)

        assert isinstance(ret, swap.agents.subject.Subject)
        assert ret.score == 0.12

    @patch.object(control.OnlineControl, 'run')
    @patch.object(GoldGetter, 'golds', {})
    @patch.object(Classifications, 'insert', MagicMock())
    @patch.object(Classifications, 'exists', MagicMock(return_value=True))
    @patch('swap.config.back_update', False)
    @patch('swap.config.database.name', 'swapDBtest')
    @patch('swap.config.parser.annotation.task', 'T1')
    @patch('swap.config.parser.annotation.true', [1])
    @patch('swap.config.parser.annotation.false', [0])
    def test_classify_rejects_reclassify(self, run):
        DB._reset()
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(self.mock_classification)

        assert ret is None

    @patch('swap.config.online_swap.workflow', '1234')
    @patch('swap.config.online_swap.caesar.host', 'example.com')
    @patch('swap.config.online_swap.caesar.port', '2000')
    def test_reducer_address(self):
        address = 'https://example.com:2000/' \
                  'workflows/1234/reducers/swap/reductions'
        assert Address.reducer() == address

    @patch('swap.config.online_swap.workflow', '1234')
    @patch('swap.config.online_swap.caesar.host', 'example.com')
    @patch('swap.config.online_swap.caesar.port', '2000')
    def test_root_address(self):
        address = 'https://example.com:2000/' \
                  'workflows/1234'
        assert Address.root() == address

    @patch('swap.config.online_swap._auth_key', 'TEST')
    def test_classify_address(self):
        address = 'https://caesar:TEST@northdown.spa.umn.edu:443/classify'
        assert Address.swap_classify() == address

    @patch('swap.config.online_swap.caesar.reducer', 'name')
    @patch('swap.config.online_swap._auth_key', 'TEST')
    def test_config_caesar(self):
        addr = Address.swap_classify()
        data = {'workflow': {
            'extractors_config': {'ext': {'type': 'external', 'url': addr}},
            'reducers_config': {'name': {'type': 'external'}},
            'rules_config': []
        }}

        assert Requests.config_caesar() == data

    def test_recent_cl_full(self):
        api = app.API(None)
        api._recent_cl = list(range(10))

        api._is_recent_cl({'id': 12})

        compare = list(range(1, 10)) + [12]
        assert api._recent_cl == compare

    def test_recent_cl_false(self):
        api = app.API(None)

        assert api._is_recent_cl({'id': 1}) is False
        assert api._recent_cl == [1]

    def test_recent_cl_true(self):
        api = app.API(None)

        api._is_recent_cl({'id': 1})
        assert api._is_recent_cl({'id': 1}) is True
        assert api._recent_cl == [1]
