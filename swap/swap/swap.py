################################################################
# SWAP implementation
#

from swap.agents.bureau import Bureau
from swap.agents.agent import Stats
from swap.agents.subject import Subject
from swap.agents.user import User
from swap.config import Config
from swap.utils import ScoreExport, Classification

from swap.db import classifications as db


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
    def classify(self, cl, subject=True, user=True):
        """
            Processes a single classification

            Args:
                cl: (dict,Classification) classification
        """
        # if subject is gold standard and gold_updates are specified,
        # update user success probability

        if not isinstance(cl, Classification):
            cl = Classification.generate(cl)

        # if self.gold_updates and cl.gold() in [0, 1]:
        # ^ moved gold check downstream to update methods
        # User and subject agents weren't being created
        # if the subject's gold label is -1
        if subject:
            self.classify_subject(cl)
        if user:
            self.classify_user(cl)

    def classify_user(self, cl):
        """
            Update User Data - Process current classification

            Args:
                cl: (Classification)
        """

        user = self.users.get(cl.user)
        subject = self.subjects.get(cl.subject)
        # if self.gold_updates and subject.isgold():
        if subject.isgold():
            user.classify(cl, subject)

    def classify_subject(self, cl):
        """
            Pass a classification to the appropriate subject agent

            Args:
                cl: (dict) classification
        """

        # Get subject and user agents
        user = self.users.get(cl.user)
        subject = self.subjects.get(cl.subject)
        # process the classification
        subject.classify(cl, user)

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

    def set_gold_labels(self, golds):
        """
            Defines the subjects explicitly that should be
            treated as gold standards

            Note: To get proper test/train split, the gold_labels
            still need to be stripped out of the classification dicts.
            This function is for defining all subjects that are
            gold on initialization

            Args:
                subjects: (dict: {subject: gold}) list of subjects
        """
        for id_, gold in golds.items():
            # TODO use old swap score or reset with p0 for bootstrap?
            # if id_ in self.subjects:
            self.subjects.get(id_, make_new=True).set_gold_label(gold)
            # else:
            #     subject = Subject(id_, self.p0, gold)
            #     self.subjects.addAgent(subject)

    @property
    def golds(self):
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
        """
        raise DeprecationWarning
        return {
            'users': self.users.export(),
            'subjects': self.subjects.export(),
            'stats': self.stats.export()
        }

    def score_export(self):
        return ScoreExport(self)

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

        db_golds = db.getAllGolds()

        data = []
        for id_, gold in db_golds.items():
            if (labels is None or id_ in labels) and \
                    gold in [0, 1] and \
                    id_ in self.subjects:
                score = self.subjects.get(id_, make_new=False).score
                data.append((gold, score))

        return data

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

        config = Config()

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
