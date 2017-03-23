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
    # > db.classifications.aggregate([{$group:{_id:'$subject_id'}},{$sample:{size:5}}])
    gold_subjects = [3328040, 3313220, 2977121, 2943566, 3317607]
    gold_subjects += [3624432, 3469678, 3287492, 3627326, 3724438]

    db = DB()
    golds = db.getExpertGold(gold_subjects)
    print(golds)

    control = BootstrapControl(.01, .5, golds)
    ui.run(control)


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


class BootstrapCursor:
    def __init__(self, db, golds):
        # Create the gold cursor
        # Create the cursor for all remaining classifications

        fields = ['user_name', 'subject_id', 'annotation', 'gold_label']
        query = Query().match('subject_id', golds).project(fields)
        cursor1 = db.getClassifications(query)

        fields = ['user_name', 'subject_id', 'annotation']
        query = Query().match('subject_id', golds, eq=False)
        # query._pipeline.append({'$match': {'classification_id': {'$lt': 1321700}}})
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
