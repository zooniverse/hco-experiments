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

        self.metrics = Bootstrap_Metrics()

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

        self.addMetric()

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

    def roc_export(self, i=None):
        bureau = self.bureau
        cursor = db.aggregate([
            {'$match': {'gold_label': {'$ne': -1}}},
            {'$group': {'_id': '$subject_id', 'gold':
                        {'$first': '$gold_label'}}},
        ])

        for item in cursor:
            subject = item['_id']
            if subject in bureau:
                bureau.getAgent(subject).gold = item['gold']

        data = []
        for s in bureau:
            if s.gold != -1:
                if i is None:
                    data.append((s.gold, s.score))
                else:
                    data.append((s.gold, s.getHistory()[i]))

        return data

    def addMetric(self):
        metric = Bootstrap_Metric(self, self.n)
        self.metrics.addMetric(metric)

    def getMetric(self, i):
        return self.metrics.get(i)

    def printMetrics(self):
        for m in self.metrics:
            print(m.num_silver())

    def manifest(self):
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


class Bootstrap_Metrics:
    def __init__(self):
        self.metrics = []

    def __str__(self):
        s = ''
        for metric in self.metrics:
            s += '%s\n' % str(metric)

        return s

    def __repr__(self):
        s = ''
        for metric in self.metrics:
            s += '%s\n' % repr(metric)

        return s

    def addMetric(self, metric):
        self.metrics.append(metric)

    def get(self, i=None):
        if i is None:
            return self.metrics[:]
        else:
            return self.metrics[i]


class Bootstrap_Metric:
    def __init__(self, bootstrap, num):
        self.num = num
        self.silver = bootstrap.silver.copy()
        self.iteration = bootstrap.n

    def __str__(self):
        return '%2d %8d %8d %8d' % \
               (self.iteration, *self.num_silver())

    def __repr__(self):
        return str((self.iteration, *self.num_silver()))

    def num_silver(self):
        count = [0, 0]
        silver = self.silver

        for silver in silver.values():
            count[silver] += 1

        remaining = db.getNSubjects() - sum(count)

        return (count[0], count[1], remaining)

    def getsilver(self):
        return self.silver


class BootstrapControl(Control):

    def __init__(self, p0, epsilon, golds):
        self.golds = golds

        super().__init__(p0, epsilon)

        # bureau = self.swap.subjects
        # print(bureau)
        # for subject, label in golds:
        #     agent = Subject(subject, p0, label)
        #     bureau.addAgent(agent)
        # self.swap.subjects = bureau

    def getClassifications(self):
        golds = [item[0] for item in self.golds]
        return BootstrapCursor(golds)

    # def _n_classifications(self):
    #     golds = [x[0] for x in self.golds]
    #     query = [
    #         {'$match': {'subject_id': {'$in': golds}}},
    #         {'$group': {'_id': 1, 'sum': {'$sum': 1}}}
    #     ]

    #     count = self._db.classifications.aggregate(query).next()['sum']
    #     count += self._db.classifications.count()

    #     return count

    def _delegate(self, cl):
        if cl.isGold():
            self.swap.processOneClassification(cl, user=True, subject=False)
        else:
            self.swap.processOneClassification(cl, user=False, subject=True)

    def getGoldLabels(self):
        return self.golds


class BootstrapCursor(Cursor):
    def __init__(self, golds):
        super().__init__(None, db.collection)
        # Create the gold cursor
        # Create the cursor for all remaining classifications

        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']
        query = Query().match('subject_id', golds).project(fields)
        cursor1 = db.getClassifications(query)

        fields = ['user_name', 'subject_id', 'annotation']

        query = Query()
        query.project(fields)
        cursor2 = db.getClassifications(query)

        self.cursors = (cursor1, cursor2)
        self.state = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        # First iterate through gold cursor
        # Iterate through other cursor once gold is depleted
        # http://anandology.com/python-practice-book/iterators.html#the-iteration-protocol
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


class Bootstrap_Analysis:
    def __init__(self, bootstrap):
        pass

    def trace_one(self, subject):
        pass
