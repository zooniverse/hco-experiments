#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels

from swap.control import Control
from swap.mongo.query import Query
from swap.mongo.db import DB, Cursor
from swap.agents.subject import Subject
from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.bureau import Bureau

from swap import ui

gold_1 = [3328040, 3313220, 2977121, 2943566, 3317607]
gold_0 = [3624432, 3469678, 3287492, 3627326, 3724438]

p0 = 0.12
epsilon = 0.5


class Interface(ui.Interface):

    def __init__(self):
        super().__init__()
        self.p0 = p0
        self.epsilon = epsilon

    def call(self):
        data = super().call()
        args = self.getArgs()

        save_name = False
        if args.saveb:
            save_name = args.saveb[0]

        if args.loadb:
            bootstrap = ui.load_pickle(args.loadb[0])
            bootstrap._deserialize()
        else:
            bootstrap = None

        if args.threshold:
            self.threshold(data, args.threshold)

        if args.iterate:
            bootstrap = self.iterate(args.iterate, save_name)

        if args.traces and bootstrap:
            self.plot_bootstrap(bootstrap, args.traces[0])

        return data

    def options(self):
        parser = super().options()

        parser.add_argument(
            '--threshold', nargs=2,
            help='Print the number of subjects above or below the threshold')

        parser.add_argument(
            '--iterate', nargs=3,
            help='Iterate through SWAP with the specified thresholds')

        parser.add_argument(
            '--traces', nargs=1)

        parser.add_argument(
            '--loadb', nargs=1,
            help='load a pickled bootstrap from file')

        parser.add_argument(
            '--saveb', nargs=1,
            help='load a pickled bootstrap from file')

        parser.add_argument(
            '--histogram', nargs=1,
            help='Draw a histogram of bootstrap data')

        parser.add_argument(
            '--broc', nargs=2, action='append',
            help='Generate ROC curve from this file, bootstrap specific')

        return parser

    def _control(self):
        golds = gold_0 + gold_1
        golds = DB().getExpertGold(golds)
        return BootstrapControl(self.p0, self.epsilon, golds.items())

    def save(self, bootstrap, fname):
        bootstrap._serialize()
        super().save(bootstrap, self.f(fname))

        with open(self.f('manifest'), 'w') as file:
            file.write(bootstrap.manifest())

    def threshold(self, data, threshold):
        min = float(threshold[0])
        max = float(threshold[1])
        high = 0
        low = 0
        other = 0

        for subject, item in data['subjects'].items():
            if item['score'] < min:
                low += 1
            elif item['score'] > max:
                high += 1
            else:
                other += 1

        print('high: %d, low: %d, other: %d' % (high, low, other))

    def iterate(self, threshold, fname=False):
        low = float(threshold[0])
        high = float(threshold[1])
        n = int(threshold[2])
        bootstrap = Bootstrap(low, high, self.p0, self.epsilon)

        for i in range(n):
            swap = bootstrap.step()
            img = self.f('iterate-%d.png' % i)
            ui.plot_subjects(swap, img)

        if fname:
            self.save(bootstrap, fname)

        return bootstrap

    def plot_bootstrap(self, bootstrap, fname):
        plot_data = []
        for subject, value in bootstrap.export().items():
            if subject in bootstrap.golds:
                c = bootstrap.golds[subject]
            else:
                c = 2

            history = value['history']
            plot_data.append((c, history))

        fname = self.f(fname)
        ui.plot_tracks(plot_data, "Bootstrap Traces", fname, scale='linear')

    def collect_roc(self, args):
        labels, data, plot_file = super().collect_roc(args)

        if args.loadb:
            bootstrap = ui.load_pickle(args.loadb[0])
            for label, i in args.broc:
                i = int(i) - 1
                labels.append(label)
                data.append(bootstrap.roc_export(i))

        return labels, data, plot_file


class Bootstrap:

    def __init__(self, t_low, t_high, p0=p0, epsilon=epsilon, export=None):
        golds = gold_0 + gold_1
        self.db = DB()
        self.golds = self.db.getExpertGold(golds)
        self.t_low = t_low
        self.t_high = t_high

        self.bureau = Bureau(Bootstrap_Subject)

        self.metrics = Bootstrap_Metrics()

        self.p0 = p0
        self.epsilon = epsilon

        self.it = 0

    def _serialize(self):
        self.db = None

    def _deserialize(self):
        self.db = DB()

    def step(self):
        self.it += 1

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
            if bureau.has(subject):
                agent = bureau.getAgent(subject)
            else:
                agent = Bootstrap_Subject(subject)
                bureau.addAgent(agent)

            agent.add(item['score'])

    def silver_update(self, export):
        golds = self.golds
        low = self.t_low
        high = self.t_high

        for subject, item in export['subjects'].items():
            if subject not in golds:
                if item['score'] < low:
                    golds[subject] = 0
                elif item['score'] > high:
                    golds[subject] = 1

        self.golds = golds

    def gen_control(self):
        return BootstrapControl(self.p0, self.epsilon, self.golds.items())

    def export(self):
        return self.bureau.export()

    def roc_export(self, i=None):
        bureau = self.bureau
        cursor = DB().classifications.aggregate([
            {'$match': {'gold_label': {'$ne': -1}}},
            {'$group': {'_id': '$subject_id', 'gold':
                        {'$first': '$gold_label'}}},
        ])

        for item in cursor:
            subject = item['_id']
            if bureau.has(subject):
                bureau.getAgent(subject).gold = item['gold']

        data = []
        for s in bureau:
            if s.gold != -1:
                if i is None:
                    data.append((s.gold, s.getScore()))
                else:
                    data.append((s.gold, s.getHistory()[i]))

        return data

    def addMetric(self):
        metric = Bootstrap_Metric(self.it, self)
        self.metrics.addMetric(metric)

    def printMetrics(self):
        for m in self.metrics:
            print(m.num_golds())

    def manifest(self):
        s = ''
        s += 'p0:         %f\n' % self.p0
        s += 'epsilon     %f\n' % self.epsilon
        s += 'iterations: %d\n' % self.it
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

    def get(self):
        return self.metrics[:]


class Bootstrap_Metric:
    def __init__(self, it, bootstrap):
        self.iteration = it
        golds = {}
        for k, v in bootstrap.golds.items():
            golds[k] = v
        self.golds = golds

    def __str__(self):
        return '%2d %8d %8d %8d' % \
               (self.iteration, *self.num_golds())

    def __repr__(self):
        return str((self.iteration, *self.num_golds()))

    # def __repr__(self):

    def num_golds(self):
        count = [0, 0]
        golds = self.golds

        for gold in golds.values():
            count[gold] += 1

        remaining = DB().getNSubjects() - sum(count)

        return (count[0], count[1], remaining)

    def getGolds(self):
        return self.golds


class BootstrapControl(Control):

    def __init__(self, p0, epsilon, golds):
        super().__init__(p0, epsilon)
        self.golds = golds

        bureau = self.swap.subjects
        for subject, label in golds:
            agent = Subject(subject, p0, label)
            bureau.addAgent(agent)
        self.swap.subjects = bureau

    def getClassifications(self):
        golds = [item[0] for item in self.golds]
        return BootstrapCursor(self._db, golds)

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
        if cl.gold() in [0, 1]:
            self.swap.processOneClassification(cl, user=True, subject=False)
        else:
            self.swap.processOneClassification(cl, user=False, subject=True)


class BootstrapCursor(Cursor):
    def __init__(self, db, golds):
        super().__init__(None, db.classifications)
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


def main():
    interface = Interface()
    ui.run(interface)


if __name__ == "__main__":
    main()
