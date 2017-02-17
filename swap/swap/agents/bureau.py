################################################################
# Keeps track of all user and subject agents
# - Initial class to test SWAP


class Bureau(object):
    """ Bureau to keep track of all agents of a specific type
    """

    def __init__(self, agent_type):
        # type of agents, just a string? (e.g. users, subjects, machines,...)
        # maybe not required because we could look at the agents' subclass
        self.agent_type = agent_type
        
        # dictionary to store all agents, key is agent-ID
        self.agents = dict()
        
    
    def addAgent(self, agent):
        """ Add agent to bureau
        
        Parameter:
        ----------
            agent: agent object
        """
        if not agent.getID() in self.agents:
            self.agents[agent.getID()] = agent
        else:
            raise KeyError("Agent-ID already in bureau, remove first")

    
    def getAgent(self,agent_id):
        """ Get agent from bureau
        
        Parameter:
        ----------
            agent_id: id of agent
        """
        try:
            return self.agents[agent_id]
        except KeyError:
            print("Error: Agent_id not in Bureau")
            
        
    def removeAgent(self,agent_id):
        """ Remove agent from bureau
        
        Parameter:
        ----------
            agent_id: id of agent
        """
        self.agents.pop(agent_id, None)
        
    def isAgentInBureau(self,agent_id):
        """ Check if agent is in bureau
        
        Parameter:
        ----------
            agent_id: id of agent
            
        Returns:
        --------
            boolean
        """
        return agent_id in self.agents