################################################################
# Parent class for all agents

import swap.agents.ledger as ledger

import abc
import statistics as st

import logging
logger = logging.getLogger(__name__)


class Agent(metaclass=abc.ABCMeta):
    """ Agent to represent a classifier (user,machine) or a subject

    Parameters:
        id: str
            Identifier of Agent
        probability: num
            Initial probability used depending on subclass.
    """

    def __init__(self, id_, ledger_type):
        self._id = id_
        self.ledger = ledger_type(id_)

    @property
    def id(self):
        return self._id

    @property
    def score(self):
        """
            Score getter function
        """
        try:
            return self.ledger.score
        except ledger.StaleException:
            return self.ledger._score

    @abc.abstractmethod
    def classify(self, cl):
        pass

    @staticmethod
    def stats(bureau):
        """
            Calculate the mean, standard deviation, and median
            of the scores in a bureau containing Agents
        """
        p = [agent.score for agent in bureau]
        return Stat(p)

    def __str__(self):
        return 'id %s transactions %d' % \
            (str(self.id), len(self.ledger.transactions))

    def __repr__(self):
        return '%s agent id %s transactions %d' % \
            (type(self), str(self.id), len(self.ledger.transactions))


class BaseStat:
    pass


class Stat(BaseStat):
    """
        Keeps track of statistics in a dataset
    """

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


class MultiStat(BaseStat):
    """
        Keeps track of statistics for multiple classes in a single
        category. For example, the 0 and 1 scores of each user agent.
    """

    def __init__(self, *data):
        stats = {}
        for label, p in data:
            stats[label] = Stat(p)
        self.stats = stats

    def add(self, label, stat):
        self.stats[label] = stat

        return self

    def addNew(self, label, data):
        self.add(label, Stat(data))

    def export(self):
        export = {}
        for label, stat in self.stats.items():
            export[label] = stat.export()

        return export

    def __str__(self):
        s = ''
        for label, stat in self.stats.items():
            s += 'stat %s %s\n' % (str(label), str(stat))
        return s


class Stats:
    """
        A collection of multiple BaseStat objects
    """

    def __init__(self):
        self.stats = {}

    def add(self, name, stat):
        if not isinstance(stat, BaseStat):
            raise TypeError('Stat must be of type BaseStat')
        self.stats[name] = stat

        return self

    def get(self, name):
        if name not in self.stats:
            raise KeyError('%s not a valid stat name' % name)
        return self.stats[name]

    def export(self):
        export = {}
        for name, stat in self.stats.items():
            export[name] = stat.export()

    def __str__(self):
        s = ''
        stats = sorted(self.stats.items(), key=lambda item: item[0])
        for name, stat in stats:
            name = str(name)
            s += '%s\n' % name
            s += ''.join(['-' for c in name])
            s += '\n'
            s += '%s\n' % str(stat)
        return s


class Accuracy:
    """
        Class to keep track of accuracy for multiple classes
    """

    def __init__(self):
        self.stats = {}

    def add(self, label, matched, n):
        """

            label:   Label of class (0, 1 for SNHunters)
            matched: Number of correct matchings
            n:       Number of total matchings
        """

        if matched > n:
            raise ValueError('Number of correct matches greater ' +
                             'than total number of matches: %d > %d' %
                             (matched, n))
        self.stats[label] = (matched, n)

    def total(self):
        """
            Returns the total accuracy accross all trackers:
                Sum of all numerators and denominators
        """
        matched = 0
        total = 0
        for m, n in self.stats.values():
            matched += m
            total += n
        return matched, total

    @staticmethod
    def score(num, den):
        """
            Gets numerical representation of an accuracy fraction.
            Returns 0 if dividing by 0
        """
        try:
            return num / den
        except ZeroDivisionError:
            logger.critical('Caught attempt to divide by zero!')
            return 0

    def __str__(self):
        s = ''
        format_ = '%5s %6d / %6d %2.2f\n'
        for label in self.stats:
            m, n = self.stats[label]
            s += format_ % (str(label), m, n, self.score(m, n))

        total = self.total()
        total_score = self.score(*total)
        s += format_ % ('total', *total, total_score)

        return s
