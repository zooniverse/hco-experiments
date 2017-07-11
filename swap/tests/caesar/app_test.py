
import swap.caesar.control as control
import swap.caesar.app as app
from swap.caesar.utils.address import Address
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
    @patch('swap.config.parser.annotation.true', [1])
    @patch('swap.config.parser.annotation.false', [0])
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
    @patch('swap.config.parser.annotation.true', [1])
    @patch('swap.config.parser.annotation.false', [0])
    def test_classify(self, run):
        DB._reset()
        oc = control.OnlineControl()
        oc.init_swap()
        ret = oc.classify(self.mock_classification)

        assert isinstance(ret, swap.agents.subject.Subject)
        assert ret.score == 0.12

    @patch('swap.config.online_swap.workflow', '1234')
    def test_reducer_address(self):
        address = 'https://caesar-staging.zooniverse.org:443/' \
                  'workflows/1234/reducers/swap/reductions'
        assert Address.reducer() == address

    @patch('swap.config.online_swap.workflow', '1234')
    def test_root_address(self):
        address = 'https://caesar-staging.zooniverse.org:443/' \
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

        assert Address.config_caesar() == data
