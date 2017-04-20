################################################################
# Keeps track of all user and subject agents
# - Initial class to test SWAP

from swap.agents.agent import Agent


class Bureau(object):
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

    @property
    def agents(self):
        return self._agents.copy()

    def addAgent(self, agent):
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
        if not agent.getID() in self._agents:
            self._agents[agent.getID()] = agent
        else:
            raise KeyError("Agent-ID already in bureau, remove first")

    def add(self, agent):
        self.addAgent(agent)

    def getAgent(self, agent_id):
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
        else:
            raise KeyError("Error: Agent_id not in Bureau")

    def get(self, agent_id):
        return self.getAgent(agent_id)

    def getAgentIds(self):
        return set(self._agents.keys())

    def removeAgent(self, agent_id):
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

    def export(self):
        data = dict()
        for name, agent in self._agents.items():
            data[name] = agent.export()
        return data

    def __iter__(self):
        return iter(self._agents.values())

    def __contains__(self, item):
        if isinstance(item, Agent):
            id_ = item.getID()
        else:
            id_ = item

        return self.has(id_)

    def __str__(self):
        return '\n'.join([str(item) for item in self._agents.values()])
