#!/usr/bin/env python
################################################################
# Recursive swap implementation to bootstrap silver-standard
# subject labels

from swap.control import Control
from swap.mongo.query import Query
from swap.mongo.db import DB
from swap.agents.subject import Subject

from swap import ui

from pprint import pprint


def main():
    def control_callback():
        # TODO allow callback to receive golds as arg
        return BootstrapControl(.01, .5, golds)

    def suite_callback(data, *args):
        print(args)
        if args[0] == 'threshold':
            args = args[1].split(',')

            high = 0
            low = 0
            other = 0

            for subject, item in data['subjects'].items():
                if item['score'] < float(args[0]):
                    low += 1
                elif item['score'] > float(args[1]):
                    high += 1
                else:
                    other += 1

            print('high: %d, low: %d, other: %d' % (high, low, other))

        elif args[0] == 'iterate':
            args = args[1].split(',')
            min = float(args[0])
            max = float(args[1])

            for subject, item in data['subjects'].items():
                if item['gold_label'] in [0, 1]:
                    continue
                if item['score'] < min:
                    golds.append((subject, 0))
                elif item['score'] > max:
                    golds.append((subject, 1))

            print(len(golds))
            ui.run(control_callback, args=[
                '-p', 'pickle2.pkl'])

    # > db.classifications.aggregate([{$group:{_id:'$subject_id'}},{$sample:{size:5}}])
    gold_subjects = [3328040, 3313220, 2977121, 2943566, 3317607]
    gold_subjects += [3624432, 3469678, 3287492, 3627326, 3724438]

    db = DB()
    golds = db.getExpertGold(gold_subjects)
    print(golds)

    ui.run(control_callback, callback=suite_callback)


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
