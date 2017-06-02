#!/usr/bin/env python
################################################################
# Metric tracking for bootstrap iterations
from swap.agents.agent import Accuracy
import swap.db.classifications as db


class Metrics:
    def __init__(self):
        self.metrics = []

    def __str__(self):
        boot = ''
        stats = ''
        thresholds = 'Thresholds\n' + \
                     '=========='
        for metric in self.metrics:
            boot += '%s\n' % str(metric)

            stats += 'Stats round %d\n' % metric.num
            stats += '=============\n'
            stats += str(metric.stats) + '\n'
            stats += 'Accuracy\n' + \
                     '--------\n'
            stats += str(metric.accuracy)

            thresholds += '%d %f < p < %f\n' % (metric.num, *metric.thresholds)

        return '%s\n\n%s\n\n%s' % (thresholds, boot, stats)

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


class Metric:
    def __init__(self, bootstrap, swap, num):
        self.num = num
        self.silver = bootstrap.silver.copy()
        self.iteration = bootstrap.n
        self.stats = swap.stats
        self.accuracy = self.silver_accuracy()

        self.thresholds = (bootstrap.t_low, bootstrap.t_high)

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

    def getSilverNames(self):
        return list(self.silver)

    def silver_accuracy(self):
        accuracy = Accuracy()
        silvers = self.silver
        real = db.getExpertGold(list(silvers))

        match = {0: 0, 1: 0, -1: 0}
        n = {0: 0, 1: 0, -1: 0}
        for id_, gold in real.items():
            if silvers[id_] == gold:
                match[gold] += 1
            n[gold] += 1

        for label in match:
            accuracy.add(label, match[label], n[label])

        return accuracy


class Bootstrap_Analysis:
    def __init__(self, bootstrap):
        pass

    def trace_one(self, subject):
        pass
