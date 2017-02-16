################################################################
# Test functions for agent class

from swap.agent import Agent

def test_init():
    a = Agent('user',.5)

    assert a.user_name == 'user'
    assert a.epsilon == .5