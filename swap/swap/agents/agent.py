################################################################
# Parent class for all agents

import abc
import statistics as st

from swap.agents.tracker import Tracker


class Agent(metaclass=abc.ABCMeta):
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

        self.annotations = Tracker()

    def getID(self):
        """ Returns Agents ID """
        return self.id

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Agents
        """
        p = [agent.getScore() for agent in bureau]
        return Stat(p)

    @abc.abstractmethod
    def export(self):
        """
            Abstract method to export agent data
        """
        return


class Stat:
    def __init__(self, data):
        self.mean = st.mean(data)
        self.median = st.median(data)
        self.stdev = st.pstdev(data)

    def export(self):
        return {'mean': self.mean,
                'stdev': self.stdev,
                'median': self.median}

    def __str__(self):
        return 'mean: %.4f median %.4f stdev %.4f' % \
            (self.mean, self.median, self.stdev)


class Stats:
    def __init__(self):
        self.stats = {}

    def add(self, key, stat):
        self.stats[key] = stat

        return self

    def addNew(self, key, data):
        self.add(key, Stat(data))

    def export(self):
        export = {}
        for key, stat in self.stats.items():
            export[key] = stat.export()

    def __str__(self):
        s = ''
        for key, stat in self.stats.items():
            s += 'stat %s %s\n' % (str(key), str(stat))
        return s
