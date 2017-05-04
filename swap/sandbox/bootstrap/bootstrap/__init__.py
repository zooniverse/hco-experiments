#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels
from swap.control import Control
from swap.db import Cursor, Query
import swap.db.classifications as db
from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.bureau import Bureau

from bootstrap.analysis import Metric, Metrics


gold_1 = [3328040, 3313220, 2977121, 2943566, 3317607]
gold_0 = [3624432, 3469678, 3287492, 3627326, 3724438]


class Bootstrap:

    def __init__(self, t_low, t_high, p0, epsilon, export=None):
        golds = gold_0 + gold_1
        self.golds = db.getExpertGold(golds)
        self.silver = self.golds.copy()
        self.t_low = t_low
        self.t_high = t_high

        self.bureau = Bureau(Bootstrap_Subject)

        self.metrics = Metrics()

        self.p0 = p0
        self.epsilon = epsilon

        self.n = 0

    def setThreshold(self, low, high):
        self.t_low = low
        self.t_high = high

    def step(self):
        self.n += 1

        control = self.gen_control()
        control.process()

        swap = control.getSWAP()
        export = swap.export()

        self.silver_update(swap.export())
        self.update_tracking(export)

        self.addMetric(swap)

        return swap

    def update_tracking(self, export):
        bureau = self.bureau
        for subject, item in export['subjects'].items():
            if subject in bureau:
                agent = bureau.getAgent(subject)
            else:
                agent = Bootstrap_Subject(subject)
                bureau.addAgent(agent)

            agent.add(item['score'])

    def silver_update(self, export):
        silver = {}
        low = self.t_low
        high = self.t_high

        for subject, item in export['subjects'].items():
            if subject not in self.golds:
                if item['score'] < low:
                    silver[subject] = 0
                elif item['score'] > high:
                    silver[subject] = 1

        for subject, gold in self.golds.items():
            silver[subject] = gold

        self.silver = silver
        return silver

    def gen_control(self):
        return BootstrapControl(self.p0, self.epsilon, self.silver.items())

    def export(self):
        return self.bureau.export()

    def roc_export(self, i=None, labels=None):
        """
        Exports list of tuples (gold, score). Useful when
        generating roc curves or evaluating performance

        i: (int) round number (0 based)
        labels: (list) list of subject identifiers. Use when limiting
                which subjects are in export
        """

        # Get real gold labels from database
        bureau = self.bureau
        golds = db.getExpertGold()

        for id_, gold in golds.items():
            if id_ in bureau:
                bureau.getAgent(id_).gold = gold

        data = []
        if labels:
            iter_ = bureau.iter_ids(labels)
        else:
            iter_ = bureau
        for s in iter_:
            if s.gold != -1:
                if i is None:
                    data.append((s.gold, s.score))
                else:
                    data.append((s.gold, s.getHistory()[i]))

        return data

    def addMetric(self, swap):
        """
        Creates a new metric for the current round from SWAP

        swap: (SWAP)
        """
        metric = Metric(self, swap, self.n)
        self.metrics.addMetric(metric)

    def getMetric(self, i):
        """
        Gets a metric for a round

        i: (int) round number of metric (0 based)
        """
        return self.metrics.get(i)

    def printMetrics(self):
        for m in self.metrics:
            print(m.num_silver())

    def manifest(self):
        """
        Generates a text manifest. Contains relevant information on the
        bootstrap run, including whatever parameters were used, and
        statistical information on each run.
        """
        s = ''
        s += 'p0:         %f\n' % self.p0
        s += 'epsilon     %f\n' % self.epsilon
        s += 'iterations: %d\n' % self.n
        s += 'thresholds: %f < p < %f\n' % (self.t_low, self.t_high)
        s += '\n'
        s += str(self.metrics)

        return s


class Bootstrap_Subject(Agent):
    def __init__(self, subject_id, gold_label=-1):
        super().__init__(subject_id, 0)
        self.gold = gold_label
        self.tracker = Tracker()

    def add(self, score):
        self.tracker.add(score)

    def export(self):
        data = {
            'score': self.tracker.current(),
            'history': self.tracker.getHistory(),
            'gold': self.gold
        }

        return data

    def getScore(self):
        return self.tracker.current()

    def getHistory(self):
        return self.tracker.getHistory()


class BootstrapControl(Control):
    """
    Feeds classifications to swap, Bootstrap specific method
    """

    def __init__(self, p0, epsilon, golds):
        """
            golds: (dict) dictionary of gold labels
        """
        self.golds = golds
        super().__init__(p0, epsilon)

    def getClassifications(self):
        golds = [item[0] for item in self.golds]
        return BootstrapCursor(golds)

    def _delegate(self, cl):
        """
        Determines if swap should only consider each classification for
        user score updates or subject score updates.
        """
        if cl.isGold():
            self.swap.processOneClassification(cl, user=True, subject=False)
        else:
            self.swap.processOneClassification(cl, user=False, subject=True)

    def getGoldLabels(self):
        return self.golds


class BootstrapCursor(Cursor):
    """
    Combines two cursors into a single continuous iterator.
    The first cursor contains all relevant silver labels,
    and is used to score the users each round. The
    second cursor contains all classifications, and
    is used to score the subjects each round
    """

    def __init__(self, golds):
        super().__init__(None, db.collection)

        # Create a cursor for gold label classifications
        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']
        query = Query().match('subject_id', golds).project(fields)
        gold_cursor = db.getClassifications(query)

        # Create a cursor for all classifications
        fields = ['user_name', 'subject_id', 'annotation']
        query = Query()
        query.project(fields)
        reg_cursor = db.getClassifications(query)

        self.cursors = (gold_cursor, reg_cursor)
        self.state = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        # First iterate through gold cursor
        # Iterate through other cursor once gold is depleted
        if self.state > 1:
            raise StopIteration()

        try:
            return self.cursors[self.state].next()
        except StopIteration:
            self.state += 1
            return self.next()

    def getCount(self):
        count = 0
        for c in self.cursors:
            count += len(c)

        return count
