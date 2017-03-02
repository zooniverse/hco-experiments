################################################################
# SWAP implementation
# - new version to work with agent / bureau classes
# - will replce SWAP when finished

from swap.agents.bureau import Bureau
from swap.agents.subject import Subject
from swap.agents.user import User


class SWAP_AGENTS(object):
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
        self.users = Bureau('users')
        self.subjects = Bureau('subjects')

        # Directive to update - if True, then a volunteer agent's posterior
        # probability of containing an interesting object will be updated
        # whenever an expertly classified "gold standard" subject is
        # classified by that volunteer.
        self.gold_updates = True

    def updateUserData(self, cl):
        """ Update User Data - Process current classification """

        # Get user agent from bureau or create a new one
        if self.users.has(cl['user_name']):
            user = self.users.getAgent(cl['user_name'])
        else:
            # create new user agent and add to bureau
            user = User(cl['user_name'], self.epsilon)
            self.users.addAgent(user)

        # process classification
        user.addClassification(cl)

    def getUserData(self):
        return self.users

    def updateSubjectData(self, cl):
        """ Update Subject Data - Process current classification """

        # check if agent is in bureau and create new one if not
        if self.subjects.has(cl['subject_id']):
            subject = self.subjects.getAgent(cl['subject_id'])
        else:
            # create new subject agent and add to bureau
            subject = Subject(cl['subject_id'], self.p0)
            self.subjects.addAgent(subject)

        # process classification
        subject.addClassification(cl)

    def getSubjectData(self):
        return self.subjects

    # Process a classification
    def processOneClassification(self, cl):
        # if subject is gold standard and gold_updates are specified,
        # update user success probability
        if (cl['gold_label'] in [0, 1] and self.gold_updates):
            self.updateUserData(cl)
        # update Subject probability
        self.updateSubjectData(cl)

if __name__ == "__main__":
    from swap import Control
    import time

    def test_swap():
        start = time.time()
        control = Control(.5, .5)
        max_batch_size = 1e5

        # get classifications
        classifications = control.getClassifications()

        n_classifications = 1e6

        # determine and set max batch size
        classifications.batch_size(int(min(max_batch_size, n_classifications)))

        swap = SWAP_AGENTS()

        # loop over classification curser to process
        # classifications one at a time
        print("Start: SWAP Processing %d classifications" % n_classifications)
        for i in range(0, n_classifications):
            # read next classification
            current_classification = classifications.next()
            # process classification in swap
            swap.processOneClassification(current_classification)
            if i % 100e3 == 0:
                print("   " + str(i) + "/" + str(n_classifications))
        print("Finished: SWAP Processing %d/%d classifications" %
              (i, n_classifications))

        control.process()
        print("--- %s seconds ---" % (time.time() - start))
        swappy = control.getSWAP()
        ud = swappy.getUserData()
        sd = swappy.getSubjectData()

    test_swap()
