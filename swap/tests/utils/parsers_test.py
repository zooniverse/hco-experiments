
import swap.utils.parsers as parsers
import swap.config as config

import datetime
import os
import csv
import pytest
import json

from unittest.mock import MagicMock, patch


def parse_test_csv():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'test_csv.csv')
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)


def parse_test_json():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'test_json.json')
    with open(path, 'r') as file:
        line = file.readline()
        return json.loads(line)


def parse_test_metadata():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'test_metadata_csv.csv')
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        return next(reader)


class Test_Parser:

    @staticmethod
    def override_annotation(task, value_key, true, false):
        c = config.parser.annotation
        c.task = task
        c.value_key = value_key
        c.true = true
        c.false = false

    def test_type_mod_int(self):
        parser = parsers.ClassificationParser(None)

        assert parser._type('1', int) == 1
        assert parser._type(1, int) == 1

    def test_type_mod_bool(self):
        parser = parsers.ClassificationParser(None)

        assert parser._type('true', bool) is True
        assert parser._type(True, bool) is True
        assert parser._type('True', bool) is True

    def test_type_mod_float(self):
        parser = parsers.ClassificationParser(None)

        assert parser._type('0.1', float) == 0.1

    def test_type_mod_timestamp(self):
        parser = parsers.ClassificationParser(None)

        t = parser._type('2017-01-24T16:11:24.680Z', 'timestamp')
        assert t == datetime.datetime(2017, 1, 24, 16, 11, 24, 680000)

        t = parser._type('2017-01-24 16:11:24 UTC', 'timestamp')
        assert t == datetime.datetime(2017, 1, 24, 16, 11, 24)

    def test_remap(self):
        field = {'type': int, 'remap': ['b', 'c', 'd', 'e']}
        parser = parsers.ClassificationParser(None)

        assert parser._remap({'a': 1}, 'a', field) == 1
        assert parser._remap({'b': 2}, 'a', field) == 2
        assert parser._remap({'c': 3}, 'a', field) == 3
        assert parser._remap({'d': 4}, 'a', field) == 4
        assert parser._remap({'e': 5}, 'a', field) == 5

    def test_remap_source(self):
        parser = parsers.ClassificationParser(None)
        field = {'type': int, 'remap': {None: 'b'}}
        cl = {'a': 1, 'b': 2}

        assert parser._remap(cl, 'a', field) == 2

    def test_remap_notsource(self):
        parser = parsers.ClassificationParser(None)
        field = {'type': int, 'remap': {'json': 'b'}}
        cl = {'a': 1, 'b': 2}

        assert parser._remap(cl, 'a', field) == 1

    def test_navigate(self):
        key = 'a.b.c'
        obj = {'a': {'b': {'c': 5}}}
        value = parsers.Parser._navigate(obj, key)

        assert value == 5

    def test_navigate_list(self):
        key = '0.1.2'
        obj = [[0,[0,0,5]]]
        value = parsers.Parser._navigate(obj, key)

        assert value == 5


class Test_Project_Parser:

    test_csv = parse_test_csv()
    test_json = parse_test_json()

    @staticmethod
    def override_annotation(task, value_key, true, false):
        c = config.parser.annotation
        c.task = task
        c.value_key = value_key
        c.true = true
        c.false = false

    def test_parse_value_1(self):
        self.override_annotation('T0', None, ['Abc'], ['Def'])
        parser = parsers.AnnotationParser(None)

        v = parser._parse_value('Abc')

        assert v == 1

    def test_parse_value_0(self):
        self.override_annotation('T0', None, ['Abc'], ['Def'])
        parser = parsers.AnnotationParser(None)

        v = parser._parse_value('Def')

        assert v == 0

    def test_parse_value_none(self):
        self.override_annotation('T0', None, ['Abc'], ['Def'])
        parser = parsers.AnnotationParser(None)

        v = parser._parse_value('ghi')

        assert v is None

    def test_parse_value_and_find(self):
        self.override_annotation('T0', '0.value.1.2.3', [5], [0])
        parser = parsers.AnnotationParser(None)

        v = parser._parse_value([
            {'value': [0,[0,0,[0,0,0,5]]]}
        ])

        assert v == 1

    def test_csv_parser_supernova(self):
        self.override_annotation(
            'T1', None,
            ['Real', 'yes', 1], ['Bogus', 'no', 0])

        from pprint import pprint
        parser = parsers.ClassificationParser('csv')
        pprint(self.test_csv[2])
        d = parser.process(self.test_csv[2].copy())

        compare = {
            'classification_id': 11423065,
            'user_id': 1437100,
            'workflow': 1737,
            'time_stamp': datetime.datetime(2016, 4, 18, 18, 50, 48),
            'session_id': 'b759eab8f4fe3436707edede3094cd5bd30c4812e2a701e48fa7cb13f0068f40',
            'live_project': False,
            'seen_before': False,
            'annotation': 1,
            'subject_id': 1935795,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)

    def test_csv_parser_seen_before(self):
        self.override_annotation(
            'T1', None,
            ['Real', 'yes', 1], ['Bogus', 'no', 0])

        from pprint import pprint
        parser = parsers.ClassificationParser('csv')
        cl = self.test_csv[3].copy()
        pprint(cl)
        d = parser.process(cl)

        compare = {
            'classification_id': 11423065,
            'user_id': 1437100,
            'workflow': 1737,
            'time_stamp': datetime.datetime(2016, 4, 18, 18, 50, 48),
            'session_id': 'b759eab8f4fe3436707edede3094cd5bd30c4812e2a701e48fa7cb13f0068f40',
            'live_project': False,
            'seen_before': True,
            'annotation': 1,
            'subject_id': 1935795,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)

    def test_csv_parser_elephant(self):
        self.override_annotation(
            'T1', None,
            ['2'], ['-1'])

        from pprint import pprint
        parser = parsers.ClassificationParser('csv')
        pprint(self.test_csv[0])
        d = parser.process(self.test_csv[0].copy())

        compare = {
            'classification_id': 25656085,
            'user_id': 1559523,
            'workflow': 3304,
            'time_stamp': datetime.datetime(2017, 1, 24, 17, 0, 38),
            'session_id': '3eb59fd166f9ace809fd1b611a52b14152e1a86f998625f7cf88f14627fa318d',
            'live_project': False,
            'seen_before': False,
            'annotation': 1,
            'subject_id': 458040,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)

    def test_csv_parser_muon_simple(self):
        self.override_annotation(
            'T1', None,
            ['Yes!'], ['No.'])

        from pprint import pprint
        parser = parsers.ClassificationParser('csv')
        pprint(self.test_csv[1])
        d = parser.process(self.test_csv[1].copy())

        compare = {
            'classification_id': 15935073,
            'user_id': 1460166,
            'workflow': 2473,
            'time_stamp': datetime.datetime(2016, 8, 22, 16, 10, 26),
            'session_id': '6049552d100cae2a9570c40bee1119cfbca4decae1e50bafffc3cba873793d6f',
            'live_project': False,
            'seen_before': False,
            'annotation': 0,
            'subject_id': 3354054,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)

    def test_csv_parser_muon_complex(self):
        self.override_annotation(
            'T0', '0.details.0.value.0',
            [3], [-1])

        from pprint import pprint
        parser = parsers.ClassificationParser('csv')
        pprint(self.test_csv[1])
        d = parser.process(self.test_csv[1].copy())

        compare = {
            'classification_id': 15935073,
            'user_id': 1460166,
            'workflow': 2473,
            'time_stamp': datetime.datetime(2016, 8, 22, 16, 10, 26),
            'session_id': '6049552d100cae2a9570c40bee1119cfbca4decae1e50bafffc3cba873793d6f',
            'live_project': False,
            'seen_before': False,
            'annotation': 1,
            'subject_id': 3354054,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)

    def test_json_parser(self):
        self.override_annotation(
            'T1', None,
            ['Real', 'yes', 1], ['Bogus', 'no', 0])

        from pprint import pprint
        parser = parsers.ClassificationParser('json')
        pprint(self.test_json)
        d = parser.process(self.test_json)

        compare = {
            'classification_id': 60910323,
            'user_id': 1437100,
            'workflow': 1737,
            'time_stamp': datetime.datetime(2017, 6, 22, 11, 29, 50, 609000),
            'session_id': '53244efffa0eddf43255b5f37b6b462242f39141f3373215d45054da4b1d9066',
            'live_project': True,
            'seen_before': False,
            'annotation': 1,
            'subject_id': 1053214149494,
        }

        print(d)
        for key, value in compare.items():
            print(key, value)
            assert d[key] == value

        assert len(d) == len(compare)


class Test_Metadata_Parser:

    test_metadata = parse_test_metadata()

    def test_csv(self):
        config.parser.subject_metadata = {
            'subject': {'type': int, 'remap': ['subject_id']},
            'project': {'type': int, 'remap': 'project_id'},
        }

        parser = parsers.MetadataParser('csv')
        data = self.test_metadata
        print(data)

        data = parser.process(data)
        assert data['subject'] == 3353054
        assert data['project'] == 3098
        assert len(data) == 2
