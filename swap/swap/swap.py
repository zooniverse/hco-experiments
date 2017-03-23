################################################################
# SWAP implementation
#

from swap.agents import Bureau
from swap.agents.subject import Subject
from swap.agents.user import User
from pprint import pprint


class SWAP(object):
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
            cl = Classification.Generate(cl)

        # if self.gold_updates and cl.gold() in [0, 1]:
        # ^ moved gold check downstream to update methods
        # User and subject agents weren't being created
        # if the subject's gold label is -1
        if user:
            self.updateUserData(cl)
        if subject:
            self.updateSubjectData(cl)

    def updateUserData(self, cl):
        """
            Update User Data - Process current classification

            Args:
                cl: (Classification)
        """

        user = self.getUserAgent(cl.user)
        if self.gold_updates and cl.gold() in [0, 1]:
            user.addClassification(cl)

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
        if 1 or self.gold_updates and cl.gold() in [0, 1]:
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
        if self.users.has(agent_id):
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

        if self.subjects.has(agent_id):
            return self.subjects.getAgent(agent_id)
        else:
            agent = Subject(agent_id, self.p0)
            if cl:
                agent.setGoldLabel(cl.gold())

            self.subjects.addAgent(agent)
            return agent

    def getUserData(self):
        """ Get User Bureau object """
        return self.users

    def getSubjectData(self):
        """ Get Subject Bureau object """
        return self.subjects

    def setGoldSubjects(self, subjects):
        """
            Defines the subjects explicitly that should be
            treated as gold standards

            Note: To get proper test/train split, the gold_labels
            still need to be stripped out of the classification dicts.
            This function is for defining all subjects that are
            gold on initialization

            Args:
                subjects: (list: (subject, label)) list of subjects
        """
        for subject, label in subjects:
            # TODO use old swap score or reset with p0 for bootstrap?
            agent = Subject(subject, self.p0, label)
            self.subjects.addAgent(agent)

    # ----------------------------------------------------------------

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
            'subjects': self.subjects.export()
        }

    def verifyClassification(self, cl):
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


class Classification:

    def __init__(self, user, subject, annotation,
                 gold_label=-1, metadata={}):

        if type(annotation) is not int:
            raise ClValueError('annotation', int)

        if type(gold_label) is not int:
            raise ClValueError('gold_label', int)

        if type(metadata) is not dict:
            raise ClValueError('metadata', dict)

        self.user = user
        self.subject = subject
        self.annotation = annotation
        self.gold_label = gold_label
        self.metadata = metadata

    def gold(self):
        return self.gold_label

    def Generate(cl):
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

    def __init__(self, key, _type, cl={}, *args, **kwargs):
        pprint(cl)
        bad_type = type(cl[key])
        msg = 'key %s should be type %s but is %s' % (key, _type, bad_type)
        ValueError.__init__(self, msg)
