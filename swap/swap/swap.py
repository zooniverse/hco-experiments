################################################################
# SWAP implementation
#

from swap.agents.bureau import Bureau
from swap.agents.agent import Stats
from swap.agents.subject import Subject
from swap.agents.user import User
from swap.utils.scores import ScoreExport, Score
from swap.utils.history import History, HistoryExport
from swap.utils.classification import Classification

from swap.db import classifications as db

import swap.config as config

import progressbar
import logging

logger = logging.getLogger(__name__)


__doc__ = """
    SWAP:
        Calculates and updates a confusion matrix for each user, and the
        probability that a subject is an object of interest

    DummySWAP:
        Calculates the probability that a subject is an object of interest
        using only simple vote fractions
"""


class SWAP:
    """
        SWAP implementation, which calculates and updates a confusion matrix
        for each user as well as the probability that a particular subject
        contains an object of interest.

        See: Marshall et al. 2016: "Space Warps I: Crowd-sourcing the
        Discovery of Gravitational Lenses", MNRAS, 455, 1171
        (hereafter Marshall et al. 2016) for algorithm explanation.
    """

    def __init__(self):
        """
            Initialize SWAP instance
            Args:
                p0: Prior probability real - in general this is derived
                empirically by considering the occurence frequency of
                interesting objects that are expertly identified within a
                fiducial dataset. It is required to initialize the likelihood
                formulation framework for each subject prior to reception of
                the first volunteer classification.

                epsilon: Estimated volunteer performance - This is either
                set arbitrarily or might be based upon judicious assesment of
                cohort-wide volunteer performance on a similar analysis task.
                It is required to initialize the likelihood formulation
                framework for each volunteer's agent.
        """

        # initialize bureaus to manage user / subject agents
        self.users = Bureau(User)
        self.subjects = Bureau(Subject)

        # Directive to update - if True, then a volunteer agent's posterior
        # probability of containing an interesting object will be updated
        # whenever an expertly classified "gold standard" subject is
        # classified by that volunteer.
        # self.gold_updates = True

        # Directive to use gold labels from classification
        # if true, assigns the gold_label from the classification
        # whenever a new subject is created
        #
        # Useful to ignore gold_labels when doing a test/train split
        # without properly sanitizing gold labels from classifications
        # self.gold_from_cl = False

    # Process a classification
    def classify(self, cl, subject=None, user=None):
        """
            Process a classification

            Parameters
            ----------
            cl : swap.utils.classification.Classification, dict
                Classification to be processed. Should be a Classification
                object, but will also accept a dict object to generate a
                new Classification object
            subject : boolean
                Deprecated
            user : boolean
                Deprecated
        """
        # if subject is gold standard and gold_updates are specified,
        # update user success probability

        if not isinstance(cl, Classification):
            cl = Classification.generate(cl)

        if subject is not None or user is not None:
            raise DeprecationWarning(
                'controlling subject and user are ' +
                'no longer supported')

        subject = self.subjects.get(cl.subject)
        user = self.users.get(cl.user)

        if not config.back_update:
            user.ledger.recalculate()

        subject.classify(cl, user)
        user.classify(cl, subject)

        # if not config.back_update:
        #     self.process_changes()

    # def _classify_user(self, cl):
    #     """
    #         Gets the appropriate user and

    #         Parameters
    #         ----------
    #         cl: Classification
    #     """

    #     user = self.users.get(cl.user)
    #     subject = self.subjects.get(cl.subject)

    #     user.classify(cl, subject)

    # def _classify_subject(self, cl):
    #     """
    #         Pass a classification to the appropriate subject agent

    #         Parameters
    #         ----------
    #         cl : (dict) classification
    #     """

    #     # Get subject and user agents
    #     user = self.users.get(cl.user)
    #     subject = self.subjects.get(cl.subject)
    #     # process the classification
    #     subject.classify(cl, user)

    def process_changes(self):
        """
        Process changes to agent ledgers

        While classifying, scores are calculated, they are merely added to
        the ledger structures. Here the changes are committed and the new
        scores are calculated. This reduces processing time as the subject
        score calculation is dependent on the user confusion matrix. The
        user's confusion matrix is subject to change depending on the
        user's performance on gold standard subjects.

        First the user's confusion matrices are calculated based on their
        performance classifying gold standard subjects. If a user's scores
        have changed, then it notifies every subject agent it classified on
        of this change.

        Then any subject agent which is connected to a user whose score has
        changed recalculates its score.
        """

        with_bar = config.back_update

        # TODO make sure notify_agents is called on each ledger

        def run(bureau):
            if with_bar:
                name = bureau.agent_type.class_name
                logger.info('processing %s score changes', name)
                with progressbar.ProgressBar(
                        max_value=bureau.calculate_changes()) as bar:
                    bar.update(0)
                    bureau.process_changes(bar)
                logger.info('done')

            else:
                bureau.process_changes()

        logger.info('Notifying user agents of subject changes')
        self.subjects.notify_changes(self.users)

        run(self.users)

        logger.info('Notifying subject agents of user changes')
        self.users.notify_changes(self.subjects)

        run(self.subjects)

        # logger.info('processing user score changes')
        # with progressbar.ProgressBar(
        #         max_value=self.users.calculate_changes()) as bar:
        #     bar.update(0)
        #     self.users.process_changes(bar)
        # logger.info('done')

        # logger.info('processing subject score changes')
        # with progressbar.ProgressBar(
        #         max_value=self.subjects.calculate_changes()) as bar:
        #     bar.update(0)
        #     self.subjects.process_changes(bar)
        # logger.info('done')

    # def getUserAgent(self, user_id):
    #     """
    #         Get a User agent from the Bureau. Creates a new one
    #         if it doesn't exist

    #         Args:
    #             agent_id: id for the user
    #     """

    #     # TODO should the bureau generate a new agent, or should
    #     # that be handled here..?
    #     if user_id in self.users:
    #         return self.users.getAgent(user_id)
    #     else:
    #         user = User(user_id, self.epsilon)
    #         self.users.addAgent(user)
    #         return user

    # def getSubjectAgent(self, id_, cl=None):
    #     """
    #         Get a Subject agent from the Bureau. Creates a new one
    #         if it doesn't exist

    #         Args:
    #             agent_id: id for the subject
    #     """

    #     if id_ in self.subjects:
    #         return self.subjects.getAgent(id_)
    #     else:
    #         subject = Subject(id_, self.p0)
    #         if self.gold_from_cl and cl.isGold():
    #             subject.set_gold_label(cl.gold)

    #         self.subjects.addAgent(subject)
    #         return subject

    # def getUserData(self):
    #     """ Get User Bureau object """
    #     return self.users

    # def getSubjectData(self):
    #     """ Get Subject Bureau object """
    #     return self.subjects

    def set_gold_labels(self, golds, with_bar=True):
        """
            Defines the subjects explicitly that should be
            treated as gold standards

            Note: To get proper test/train split, the gold_labels
            still need to be stripped out of the classification dicts.
            This function is for defining all subjects that are
            gold on initialization

            Parameters
            ----------
            golds : dict
                (subject id : gold label) Mapping of subject to its gold label
        """
        # Removes gold label from all subjects not in the golds list
        logger.info('Processing gold labels')
        if with_bar:
            bar = progressbar.ProgressBar(max_value=len(self.subjects))
        for subject in self.subjects:
            if subject.id not in golds:
                subject.set_gold_label(-1, self.subjects, self.users)

            if with_bar:
                bar.update(bar.value + 1)
        # Assigns the new gold label to subjects in the list
        # Also tells the Bureau to make a new subject agent if it
        # doesn't exist yet
        for id_, gold in golds.items():
            subject = self.subjects.get(id_, make_new=True)
            subject.set_gold_label(gold, self.subjects, self.users)

        # self.process_changes()

    @property
    def golds(self):
        """
        Compile a list of all the subject -> gold mappings being used

        Returns
        -------
        dict
            {subject id: gold label}
        """
        data = {}
        for subject in self.subjects:
            if subject.isgold():
                data[subject.id] = subject.gold

        return data

    # ----------------------------------------------------------------

    @property
    def stats(self):
        """
            Consolidate all the statistical data from the bureaus

            Returns
            -------
            swap.agents.agent.Stats
                Stats object containing statistical data on the
                confusion matrices and subject scores
        """
        stats = Stats()
        if len(self.users) > 0:
            stats.add('user', self.users.stats())
        if len(self.subjects) > 0:
            stats.add('subject', self.subjects.stats())

        return stats

    def stats_str(self):
        """
            Consolidate all the statistical data from the bureaus
            into a string

            Returns
            -------
            str
                Stats to string
        """
        return str(self.stats)

    # def exportUserData(self):
    #     """ Exports consolidated user information """
    #     return self.users.export()

    # def exportSubjectData(self):
    #     """ Exports consolidated subject information """
    #     return self.subjects.export()

    def export(self):
        """
            Export both user and subject data

            Deprecated
        """
        raise DeprecationWarning
        return {
            'users': self.users.export(),
            'subjects': self.subjects.export(),
            'stats': self.stats.export()
        }

    def score_export(self, history=None):
        """
        Generate object containing subject score data

        Used in most of our plotting functions and other analysis tools

        Returns
        -------
        swap.utils.scores.ScoreExport
            ScoreExport
        """
        if history is None:
            history = self.history_export()

        logger.info('Generating score export')
        scores = {}
        for subject in self.subjects:
            if len(subject.ledger) == 0:
                continue
            id_ = subject.id
            score = subject.score
            scores[id_] = Score(id_, None, score)

        logger.debug('done')
        return ScoreExport(scores, history=history)

    def history_export(self):
        """
        Genearte object containing subject score history

        Returns
        -------
        swap.utils.history.HistoryExport
            HistoryExport
        """
        logger.info('Generating history export')
        history = {}
        for subject in self.subjects:
            if len(subject.ledger) == 0:
                continue

            # Generate list of subject scores
            scores = []
            for t in sorted(subject.ledger, key=lambda t: t.order):
                scores.append(t.score)

            # Create History object
            id_ = subject.id
            history[id_] = History(id_, subject.gold, scores)

        logger.debug('done')
        return HistoryExport(history)

    def roc_export(self, labels=None):
        """
            Exports subject classification data in a suitable form
            for generating a roc curve. Data consolidated into list of tuples
            Each tuble takes the form:
                (true label, probability)

            Args:
                labels: List of subject ids. Limits roc export to these
                        subjects
        """

        logger.info('Generating roc export')
        db_golds = db.getAllGolds()

        data = []
        for id_, gold in db_golds.items():
            if (labels is None or id_ in labels) and \
                    gold in [0, 1] and \
                    id_ in self.subjects:
                score = self.subjects.get(id_, make_new=False).score
                data.append((gold, score))

        return data

    def debug_str(self):
        s = ''
        for u in self.users:
            s += 'user %s\n' % str(u.id)
            s += '%s\n' % str(u.ledger)
        for a in self.subjects:
            s += 'subject %s gold %d\n' % (str(a.id), a.gold)
            s += '%s\n' % str(a.ledger)
        return s

    def manifest(self):
        """
        Generates a text manifest. Contains relevant information on the
        bootstrap run, including whatever parameters were used, and
        statistical information on each run.
        """

        def countGolds():
            golds = [0, 0, 0]
            for subject in self.subjects:
                golds[subject.gold] += 1

            return tuple(golds)

        s = ''
        s += 'SWAP manifest\n'
        s += '=============\n'
        s += 'p0:         %f\n' % config.p0
        s += 'epsilon:    %f\n' % config.epsilon
        s += '\n'
        s += 'n golds:    %d %d %d\n' % countGolds()
        s += '\n'
        s += 'Statistics\n'
        s += '==========\n'
        s += str(self.stats) + '\n'

        return s


class DummySWAP:
    """
    For each subject, calculates the probability that it is of
    interest using simple vote fractions.

    Purpose is to provide a baseline when making performance
    comparisons
    """

    def __init__(self):
        self.data = {}

    def process(self):
        """
        Process all subjects
        """
        cursor = self.get_cursor()
        for item in cursor:
            score = item['votes'] / item['total']
            gold = item['gold']
            id_ = item['_id']
            self.data[id_] = Score(id_, gold, score)

    def get_cursor(self):
        """
        Generate a cursor with classifications

        Returns
        -------
        swap.db.Cursor
            Classifications
        """
        cursor = db.aggregate([
            {'$match': {'gold_label': {'$ne': -1}}},
            {'$group': {
                '_id': '$subject_id',
                'gold': {'$first': "$gold_label"},
                'total': {'$sum': 1},
                'votes': {'$sum': "$annotation"}}}])

        return cursor

    def export(self):
        """
        Deprecated
        """
        raise DeprecationWarning
        data = {}
        for subject, item in self.data.items():
            data[subject] = {'gold': item[0], 'score': item[1]}

        return data

    def score_export(self):
        """
        Generate object containing subject score data

        Used in most of our plotting functions and other analysis tools

        Returns
        -------
        swap.utils.scores.ScoreExport
            ScoreExport
        """
        return ScoreExport(self.data, new_golds=False)
