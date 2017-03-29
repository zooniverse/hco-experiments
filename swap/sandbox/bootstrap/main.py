#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels

from swap.control import Control
from swap.mongo.query import Query
from swap.mongo.db import DB
from swap.agents.subject import Subject
from swap.agents.agent import Agent
from swap.agents.tracker import Tracker
from swap.agents.bureau import Bureau

from swap import ui

from pprint import pprint

gold_1 = [3328040, 3313220, 2977121, 2943566, 3317607]
gold_0 = [3624432, 3469678, 3287492, 3627326, 3724438]


class Interface(ui.Interface):
    def __init__(self, golds):
        super().__init__()
        self.golds = golds

    def call(self):
        data = super().call()
        args = self.getArgs()

        save_name = False
        if args.saveb:
            save_name = args.saveb

        if args.loadb:
            bootstrap = ui.load_pickle(args.loadb)

        if args.threshold:
            self.threshold(data, args.threshold)

        if args.iterate:
            self.iterate(args.iterate, save_name)

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
            '--loadb', nargs=1,
            help='load a pickled bootstrap from file')

        parser.add_argument(
            '--saveb', nargs=1,
            help='load a pickled bootstrap from file')

        return parser

    def _control(self):
        return BootstrapControl(.12, .5, self.golds.items())

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

    # def iterate(self, data, threshold):
    #     min = float(threshold[0])
    #     max = float(threshold[1])

    #     for subject, item in data['subjects'].items():
    #         if item['gold_label'] in [0, 1]:
    #             continue
    #         if item['score'] < min:
    #             self.golds[subject] = 0
    #         elif item['score'] > max:
    #             self.golds[subject] = 1

    #     print(len(self.golds))

    #     self.control = None
        
    #     fname = self.getArgs().pickle
    #     fname = fname.split('.')
    #     fname[0] += '-i'
    #     fname = '.'.join(fname)

    #     ui.run_swap(self.getControl(), fname)

    def iterate(self, threshold, fname=False):
        low = float(threshold[0])
        high = float(threshold[1])
        n = int(threshold[2])
        bootstrap = Bootstrap(low, high)

        for i in range(n):
            swap = bootstrap.step()
            ui.plot_subjects(swap, 'iterate-%d.png' % i)

        if fname:
            ui.save_pickle(bootstrap, fname)

        self.plot_bootstrap(bootstrap)

    def plot_bootstrap(self, bootstrap):
        plot_data = []
        for subject, value in bootstrap.export().items():
            if subject in bootstrap.golds:
                c = bootstrap.golds[subject]
            else:
                c = 2

            history = value['history']
            plot_data.append((c, history))

        ui.plot_tracks(plot_data, "Test", 'test-2.png', scale='linear')

        plot_data = []
        for subject in bootstrap.export().values():
            plot_data.append(subject['score'])

        ui.plot_histogram(plot_data, None, None)


class Bootstrap:

    def __init__(self, t_low, t_high, export=None):
        golds = gold_0 + gold_1
        self.db = DB()
        self.golds = self.db.getExpertGold(golds)
        self.t_low = t_low
        self.t_high = t_high

        self.bureau = Bureau(Bootstrap_Subject)

    def step(self):
        control = self.gen_control()
        control.process()

        swap = control.getSWAP()
        export = swap.export()

        self.silver_update(swap.export())
        self.update_tracking(export)

        return swap

    def next(self):
        pass

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
        return BootstrapControl(.01, .5, self.golds.items())

    def export(self):
        return self.bureau.export()


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
            'history': self.tracker.getHistory()
        }

        return data


def main():
    # > db.classifications.aggregate([{$group:{_id:'$subject_id'}},{$sample:{size:5}}])
    gold_subjects = [3328040, 3313220, 2977121, 2943566, 3317607]
    gold_subjects += [3624432, 3469678, 3287492, 3627326, 3724438]

    db = DB()
    golds = db.getExpertGold(gold_subjects)
    print(golds)
    interface = Interface(golds)

    ui.run(interface)


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

    def _n_classifications(self):
        return super()._n_classifications() * 2

    def _delegate(self, cl):
        if cl.gold() in [0, 1]:
            self.swap.processOneClassification(cl, user=True, subject=False)
        else:
            self.swap.processOneClassification(cl, user=False, subject=True)


class BootstrapCursor:
    def __init__(self, db, golds):
        # Create the gold cursor
        # Create the cursor for all remaining classifications

        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']
        query = Query().match('subject_id', golds).project(fields)
        cursor1 = db.getClassifications(query)

        fields = ['user_name', 'subject_id', 'annotation']
        # query = Query().match('subject_id', golds, eq=False)
        query = Query()
        # query._pipeline.append({'$match': {'classification_id': {'$lt': 1321700}}})
        # query.match('subject_id', golds, eq=False).project(fields)
        query.project(fields)
        cursor2 = db.getClassifications(query)

        # with open('test.log', 'w') as file:
        #     pprint(list(cursor1), file)
        #     pprint(list(cursor2), file)

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

        cursor = self.cursors[self.state]
        if cursor.alive:
            return cursor.next()
        else:
            self.state += 1
            return self.next()


def test():
    swap = Control(.01, .5)
    db = swap._db
    golds = [2149031, 2149962]

    cursor = BootstrapCursor(db, golds)
    for i in cursor:
        pprint(i)


if __name__ == "__main__":
    main()
