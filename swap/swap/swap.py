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
    def processOneClassification(self, cl):
        # if subject is gold standard and gold_updates are specified,
        # update user success probability

        self.verifyClassification(cl)

        if (cl['gold_label'] in [0, 1] and self.gold_updates):
            self.updateUserData(cl)
            # update Subject probability
            self.updateSubjectData(cl)

    def updateUserData(self, cl):
        """ Update User Data - Process current classification """

        # Get user agent from bureau or create a new one
        user = self.getUserAgent(cl['user_name'])
        user.addClassification(cl)

    def updateSubjectData(self, cl):
        """ Update Subject Data - Process current classification """

        subject = self.getSubjectAgent(cl['subject_id'])
        user = self.getUserAgent(cl['user_name'])

        # process classification
        subject.addClassification(cl, user)

    def getUserAgent(self, agent_id):
        if self.users.has(agent_id):
            return self.users.getAgent(agent_id)
        else:
            agent = User(agent_id, self.epsilon)
            self.users.addAgent(agent)
            return agent

    def getSubjectAgent(self, agent_id, cl=None):
        if self.subjects.has(agent_id):
            return self.subjects.getAgent(agent_id)
        else:
            agent = Subject(agent_id, self.p0)
            if cl and 'gold_label' in cl:
                agent.setGoldLabel(cl['gold_label'])

            self.subjects.addAgent(agent)
            return agent

    # Export User Bureau
    def getUserData(self):
        """ Get User Bureau object """
        return self.users

    # Export Subject Bureau
    def getSubjectData(self):
        """ Get Subject Bureau object """
        return self.subjects

    # Export User Information
    def exportUserData(self):
        """ Exports consolidated user information """
        return self.users.export()

    # Export Subject Information
    def exportSubjectData(self):
        """ Exports consolidated subject information """
        return self.subjects.export()

    def export(self):
        return {
            'users': self.users.export(),
            'subjects': self.subjects.export()
        }

    def verifyClassification(self, cl):
        names = [
            'user_name',
            'subject_id',
            'annotation',
            'gold_label']
        for key in names:
            try:
                cl[key]
            except KeyError:
                raise ClKeyError(key, cl)

        if type(cl['annotation']) is not int:
            raise ClValueError('annotation', int, cl)
        if type(cl['gold_label']) is not int:
            raise ClValueError('gold_label', int, cl)


class ClValidationError(ValueError):
    """
        Raise when the classification cannot be validated
    """
    pass


class ClKeyError(KeyError):
    def __init__(self, key, cl, *args, **kwargs):
        pprint(cl)
        msg = 'key %s not found in classification %s' % (key, str(cl))
        KeyError.__init__(self, msg)


class ClValueError(ValueError):
    def __init__(self, key, _type, cl, *args, **kwargs):
        pprint(cl)
        bad_type = type(cl[key])
        msg = 'key %s should be type %s but is %s' % (key, _type, bad_type)
        ValueError.__init__(self, msg)
