################################################################
# Keeps track of all user and subject agents
# - Initial class to test SWAP


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
        self.agents = dict()

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
        if not agent.getID() in self.agents:
            self.agents[agent.getID()] = agent
        else:
            raise KeyError("Agent-ID already in bureau, remove first")

    def getAgent(self, agent_id):
        """ Get agent from bureau

        Parameter:
        ----------
            agent_id: id of agent

        Returns:
        -------
            agent
        """
        if agent_id in self.agents:
            return self.agents[agent_id]
        else:
            raise KeyError("Error: Agent_id not in Bureau")

    def removeAgent(self, agent_id):
        """ Remove agent from bureau

        Parameter:
        ----------
            agent_id: id of agent
        """
        del self.agents[agent_id]

    def has(self, agent_id):
        """ Check if agent is in bureau

        Parameter:
        ----------
            agent_id: id of agent

        Returns:
        --------
            boolean
        """
        return agent_id in self.agents

    def export(self):
        data = dict()
        for agent in self.agents:
            data[agent.getID()] = agent.export()
