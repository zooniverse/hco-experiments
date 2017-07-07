
import swap.caesar.control as control
import swap.caesar.app as app
import swap.agents.subject
from swap.db import DB
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
    @patch('swap.config.database.builder.annotation.true', [1])
    @patch('swap.config.database.builder.annotation.false', [0])
    def test_classify(self, run):
        DB._reset()
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(self.mock_classification)

        assert isinstance(ret, swap.agents.subject.Subject)
        assert ret.score == 0.12

    def test_reducer_address(self):
        address = 'https://caesar-staging.zooniverse.org:443/' \
                  'workflows/1646/reducers/swap/reductions'
        assert app.Address.reducer() == address

    def test_root_address(self):
        address = 'https://caesar-staging.zooniverse.org:443/' \
                  'workflows/1646'
        assert app.Address.root() == address

    @patch('swap.config.online_swap._auth_key', 'TEST')
    def test_classify_address(self):
        address = 'https://caesar:TEST@northdown.spa.umn.edu:443/classify'
        assert app.Address.swap_classify() == address

    @patch('swap.config.online_swap.caesar.reducer', 'name')
    @patch('swap.config.online_swap._auth_key', 'TEST')
    def test_config_caesar(self):
        addr = app.Address.swap_classify()
        data = {'workflow': {
            'extractors_config': {'name': {'type': 'external', 'url': addr}},
            'reducers_config': {'name': {'type': 'external'}},
            'rules_config': []
        }}

        assert app.Address.config_caesar() == data
