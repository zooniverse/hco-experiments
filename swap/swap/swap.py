################################################################
# SWAP implementation
#

from swap.agents.bureau import Bureau
from swap.agents.agent import Stats
from swap.agents.subject import Subject
from swap.agents.user import User
from swap.utils import ScoreExport
from pprint import pprint

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

    def __init__(self, p0=0.01, epsilon=0.5):
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

        # assign class variables from args
        self.p0 = p0  # prior probability real
        self.epsilon = epsilon  # estimated volunteer performance

        # initialize bureaus to manage user / subject agents
        self.users = Bureau(User)
        self.subjects = Bureau(Subject)

        # Directive to update - if True, then a volunteer agent's posterior
        # probability of containing an interesting object will be updated
        # whenever an expertly classified "gold standard" subject is
        # classified by that volunteer.
        self.gold_updates = True

        # Directive to use gold labels from classification
        # if true, assigns the gold_label from the classification
        # whenever a new subject is created
        #
        # Useful to ignore gold_labels when doing a test/train split
        # without properly sanitizing gold labels from classifications
        self.gold_from_cl = False

    # Process a classification
    def processOneClassification(self, cl, subject=True, user=True):
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
            self.updateSubjectData(cl)
        if user:
            self.updateUserData(cl)

    def updateUserData(self, cl):
        """
            Update User Data - Process current classification

            Args:
                cl: (Classification)
        """

        user = self.getUserAgent(cl.user)
        subject = self.getSubjectAgent(cl.subject)
        if self.gold_updates and subject.hasGold():
            user.addClassification(cl, subject.gold)

    def updateSubjectData(self, cl):
        """
            Pass a classification to the appropriate subject agent

            Args:
                cl: (dict) classification
        """

        # Get subject and user agents
        subject = self.getSubjectAgent(cl.subject, cl=cl)
        user = self.getUserAgent(cl.user)

        # process the classification
        subject.addClassification(cl, user)

    def getUserAgent(self, agent_id):
        """
            Get a User agent from the Bureau. Creates a new one
            if it doesn't exist

            Args:
                agent_id: id for the user
        """

        # TODO should the bureau generate a new agent, or should
        # that be handled here..?
        if agent_id in self.users:
            return self.users.getAgent(agent_id)
        else:
            agent = User(agent_id, self.epsilon)
            self.users.addAgent(agent)
            return agent

    def getSubjectAgent(self, agent_id, cl=None):
        """
            Get a Subject agent from the Bureau. Creates a new one
            if it doesn't exist

            Args:
                agent_id: id for the subject
        """

        if agent_id in self.subjects:
            return self.subjects.getAgent(agent_id)
        else:
            agent = Subject(agent_id, self.p0)
            if self.gold_from_cl and cl.isGold():
                agent.setGoldLabel(cl.gold)

            self.subjects.addAgent(agent)
            return agent

    def getUserData(self):
        """ Get User Bureau object """
        return self.users

    def getSubjectData(self):
        """ Get Subject Bureau object """
        return self.subjects

    def setGoldLabels(self, golds):
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
        for subject, gold in golds.items():
            # TODO use old swap score or reset with p0 for bootstrap?
            if subject in self.subjects:
                self.subjects.get(subject).setGoldLabel(gold)
            else:
                agent = Subject(subject, self.p0, gold)
                self.subjects.addAgent(agent)

    def getGoldLabels(self):
        data = {}
        for subject in self.subjects:
            if subject.gold != -1:
                data[subject.id] = subject.gold

        return data

    # ----------------------------------------------------------------

    @property
    def stats(self):
        """
            Consolidate all the statistical data from the bureaus
        """
        stats = Stats()
        stats.add('user', self.users.stats())
        stats.add('subject', self.subjects.stats())

        return stats

    def stats_str(self):
        """
            Consolidate all the statistical data from the bureaus
            into a string
        """
        return str(self.stats)

    def exportUserData(self):
        """ Exports consolidated user information """
        return self.users.export()

    def exportSubjectData(self):
        """ Exports consolidated subject information """
        return self.subjects.export()

    def export(self):
        """
            Export both user and subject data
        """
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
                score = self.subjects.get(id_).score
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

        s = ''
        s += 'SWAP manifest\n'
        s += '=============\n'
        s += 'p0:         %f\n' % self.p0
        s += 'epsilon:    %f\n' % self.epsilon
        s += '\n'
        s += 'n golds:    %5d %5d %5d\n' % countGolds()
        s += '\n'
        s += 'Statistics\n'
        s += '==========\n'
        s += str(self.stats) + '\n'

        return s


class Classification:
    """
        Object to represent each individual classification
    """

    def __init__(self, user, subject, annotation,
                 gold_label=-1, metadata={}):
        """
            Args:
                user:       user name of the classifying user
                subject:    id number of the subject being classified
                annotation: label assigned by the user
                gold_label: (optional) expert assigned label
                metadata:   (optional) any additional metadata associated
        """

        if type(annotation) is not int:
            raise ClValueError('annotation', int, annotation)

        if type(gold_label) is not int:
            raise ClValueError('gold_label', int, gold_label)

        if type(metadata) is not dict:
            raise ClValueError('metadata', dict, metadata)

        self.user = user
        self.subject = subject
        self.annotation = annotation

        self.gold_label = None
        self.gold = gold_label

        self.metadata = metadata

    @property
    def gold(self):
        """
            Get the gold label
        """
        if self.gold_label is not None:
            return self.gold_label
        else:
            return False

    @gold.setter
    def gold(self, gold):
        if gold in [0, 1]:
            self.gold_label = gold
        else:
            self.gold_label = None

    def isGold(self):
        if self.gold_label is not None:
            return True
        else:
            return False

    def __str__(self):
        return 'user %s subject %s annotation %d gold %s' % \
            (str(self.user), str(self.subject),
             self.annotation, str(self.gold))

    @staticmethod
    def generate(cl):
        """
            Static generator method. Generates a classification
            object from a classification in dictionary form
        """
        Classification.Validate(cl)

        user = cl['user_name']
        subject = cl['subject_id']
        annotation = cl['annotation']

        c = Classification(user, subject, annotation)

        if 'gold_label' in cl:
            c.gold_label = cl['gold_label']

        if 'metadata' in cl:
            c.metadata = cl['metadata']

        return c

    def Validate(cl):
        """
            Verify classification is compatible with current
            SWAP version

            Args:
                cl: (dict) classification
        """
        names = [
            'user_name',
            'subject_id',
            'annotation']
        for key in names:
            try:
                cl[key]
            except KeyError:
                raise ClKeyError(key, cl)

        if type(cl['annotation']) is not int:
            raise ClValueError('annotation', int, cl)
        if 'gold_label' in cl and type(cl['gold_label']) is not int:
            raise ClValueError('gold_label', int, cl)


class ClKeyError(KeyError):
    """
        Raise when a classification is missing a key element
    """

    def __init__(self, key, cl={}, *args, **kwargs):
        pprint(cl)
        msg = 'key %s not found in classification %s' % (key, str(cl))
        KeyError.__init__(self, msg)


class ClValueError(ValueError):
    """
        Raise when a value in the classification is incorrect,
        impossible, or is of the wrong type
    """

    def __init__(self, key, _type, value, *args, **kwargs):
        if type(value) is dict:
            kwargs['cl'] = value
            value = value[key]
        if 'cl' in kwargs:
            pprint(kwargs['cl'])
        bad_type = type(value)
        msg = 'key %s should be type %s but is %s' % (key, _type, bad_type)
        ValueError.__init__(self, msg)
