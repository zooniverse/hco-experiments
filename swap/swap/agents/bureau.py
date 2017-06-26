################################################################
# Keeps track of all user and subject agents
# - Initial class to test SWAP

from swap.agents.agent import Agent
from swap.utils import Singleton


class Bureau:
    """ Bureau to keep track of agents

    Parameter:
    ----------
        agent_type: str
            Informative string to indicate agent types in that specific bureau
    """

    def __init__(self, agent_type):
        # type of agents, just a string? (e.g. users, subjects, machines,...)
        # maybe not required because we could look at the agents' subclass

        # What if we pass the type of the agents here... as in Bureau(Subject)
        # or Bureau(User) etc. ?
        self.agent_type = agent_type
        # dictionary to store all agents, key is agent-ID
        self._agents = dict()

    def add(self, agent, override=True):
        """
            Add agent to bureau

            Parameter:
            ----------
                agent: agent object
        """
        # Verify agent is of proper type
        if not isinstance(agent, self.agent_type):
            raise TypeError(
                'Agent type %s is not of type %s' %
                (type(agent), self.agent_type))

        # Add agent to collection
        if agent.id in self._agents and not override:
            raise KeyError("Agent-ID already in bureau, remove first")
        else:
            self._agents[agent.id] = agent

    def get(self, agent_id, make_new=True):
        """ Get agent from bureau

        Parameter:
        ----------
            agent_id: id of agent

        Returns:
        -------
            agent
        """
        if agent_id in self._agents:
            return self._agents[agent_id]
        elif make_new:
            agent = self.agent_type(agent_id)
            self.add(agent)
            return agent
        else:
            return None

    def remove(self, agent_id):
        """ Remove agent from bureau

        Parameter:
        ----------
            agent_id: id of agent
        """
        del self._agents[agent_id]

    def has(self, agent_id):
        """ Check if agent is in bureau

        Parameter:
        ----------
            agent_id: id of agent

        Returns:
        --------
            boolean
        """
        return agent_id in self._agents

    def process_changes(self, bar=None):
        for agent in self:
            if bar is not None and agent.ledger.stale:
                bar.update(bar.value + 1)

            agent.ledger.recalculate()

    def notify_changes(self, other_bureau):
        for agent in self:
            agent.ledger.notify_agents(self, other_bureau)

    def calculate_changes(self):
        return len([1 for i in self if i.ledger.stale])

    # ----------------------------------------------------------------

    def idset(self):
        return set(self._agents.keys())

    def stats(self):
        """
            Calculates the mean, standard deviation, and median
            of scores in this bureau
        """
        return self.agent_type.stats(self)

    def export(self):
        data = dict()
        for name, agent in self._agents.items():
            data[name] = agent.export()
        return data

    def iter_ids(self, ids):
        return AgentIterator(self, ids)

    def __iter__(self):
        return iter(self._agents.values())

    def __contains__(self, item):
        if isinstance(item, Agent):
            id_ = item.id
        else:
            id_ = item

        return self.has(id_)

    def __len__(self):
        return len(self._agents)

    def __str__(self):
        return '\n'.join([str(item) for item in self._agents.values()])

    def __repr__(self):
        return '%d agents of type %s' %\
            (len(self._agents), str(self.agent_type))


class AgentIterator:
    """
        Custom iterator to iterate through agents in a bureau
        according to a list of ids
    """

    def __init__(self, bureau, ids):
        self.bureau = bureau
        self.ids = ids
        self.index = 0

    def next(self):
        index = self.index
        if index >= len(self):
            raise StopIteration
        else:
            agent = self.bureau.get(self.ids[index])
            self.index += 1
            return agent

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.ids)

    def __next__(self):
        return self.next()


# class _Bureaus:
#     """
#     Central container with references to the subject and
#     user bureaus
#     """

#     def add(self, name, bureau):
#         self.setattr(name, bureau)


# class Bureaus(_Bureaus, metaclass=Singleton):
#     pass
