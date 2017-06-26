################################################################
# Test functions for bureau class

import pytest
from pprint import pprint
from swap.agents.bureau import Bureau
from swap.agents.bureau import AgentIterator
from swap.agents.agent import Agent
from swap.agents.user import User
from swap.agents.subject import Subject

import unittest


class TestBureau:

    def test_init(self):
        b = Bureau(Agent)
        assert b.agent_type is Agent
        assert b._agents == {}

    def test_add_agent_typecheck(self):
        b = Bureau(User)
        agent = Subject(0)
        with pytest.raises(TypeError):
            b.add(agent)

    def test_add_agent_twice_nonew(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)
        with pytest.raises(KeyError):
            b.add(agent, override=False)

    def test_add_agent_twice_new(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)
        b.add(agent, override=True)

    def test_add_agent(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)

        assert agent in b
        assert 0 in b._agents
        assert b.get(0) == agent

    def test_get_agent(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)

        assert b.get(0) == agent

    def test_get_agent_new(self):
        b = Bureau(User)
        u = b.get(15)

        assert type(u) is User
        assert u.id == 15

    def test_get_newagent_isadded(self):
        b = Bureau(User)
        u = b.get(15)

        assert u in b
        assert b.get(15) == u

    def test_get_agent_none(self):
        b = Bureau(User)
        assert b.get(0, make_new=False) is None

    def test_del_agent(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)
        b.remove(0)

        assert agent not in b
        assert 0 not in b._agents

    def test_has_true(self):
        b = Bureau(User)
        agent = User(0)
        b.add(agent)

        assert agent in b

    def test_has_false(self):
        b = Bureau(User)

        assert 0 not in b

    def test_contains_true(self):
        b = Bureau(User)
        agent = User(15)
        b.add(agent)
        assert agent in b

    def test_contains_false(self):
        b = Bureau(User)
        agent = User(15)
        assert agent not in b

    def test_contains_int(self):
        b = Bureau(User)
        agent = User(15)
        b.add(agent)

        assert 15 in b
        assert 16 not in b

    def test_idset(self):
        b = Bureau(User)
        [b.add(User(i)) for i in range(5)]
        assert b.idset() == set(range(5))

    def test_stats_subject(self):
        b = Bureau(Subject)
        [b.add(Subject(i)) for i in range(5)]
        [s.ledger.recalculate() for s in b]
        b.stats()

    def test_stats_users(self):
        b = Bureau(User)
        [b.add(User(i)) for i in range(5)]
        [u.ledger.recalculate() for u in b]
        b.stats()

    # ---------EXPORT TEST------------------------------
    @pytest.mark.skip()
    def test_export_contents(self):
        b = Bureau(User)
        for i in range(10):
            b.add(User(i))

        export = b.export()
        pprint(export)

        assert b.export()[0] == User(0).export()
        assert b.export()[5] == User(5).export()


class TestAgentIterator(unittest.TestCase):

    def get_bureau(self):
        b = Bureau(Subject)
        for i in range(5):
            b.add(Subject(i))

        return b

    def test_next(self):
        b = self.get_bureau()
        a = AgentIterator(b, [1, 3])

        assert next(a).id == 1
        assert next(a).id == 3
        with self.assertRaises(StopIteration):
            a.next()

    def test_length(self):
        b = self.get_bureau()
        a = AgentIterator(b, [1, 2])

        assert len(a) == 2

    def test_iter(self):
        b = self.get_bureau()
        a = AgentIterator(b, [1, 2])

        assert iter(a) == a
