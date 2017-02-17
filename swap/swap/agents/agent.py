################################################################
# Parent class for all agents


class Agent:
    """ Agent to represent a classifier (user,machine) or a subject

    Parameters:
        id: str
            Identifier of Agent
        probability: num
            Initial probability used depending on subclass.
    """

    def __init__(self, id, probability):
        self.id = id
        self.probability = probability

    def getID(self):
        """ Returns Agents ID """
        return self.id
