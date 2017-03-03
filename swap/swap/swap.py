################################################################
# SWAP implementation
#

from swap.agents import Bureau
from swap.agents.subject import Subject
from swap.agents.user import User

class SWAP(object):
    """
        SWAP implementation, which calculates and updates a confusion matrix for each user
        as well as the probability that a particular subject contains an object of interest.

        See: Marshall et al. 2016: "Space Warps I: Crowd-sourcing the Discovery of
        Gravitational Lenses", MNRAS, 455, 1171 (hereafter Marshall et al. 2016) for
        algorithm explanation.
    """

    def __init__(self, p0=0.01, epsilon=0.5):
        """
            Initialize SWAP instance
            Args:
                p0: Prior probability real - in general this is derived empirically by
                considering the occurence frequency of interesting objects that are expertly
                identified within a fiducial dataset. It is required to initialize the likelihood
                formulation framework for each subject prior to reception of the first
                volunteer classification.

                epsilon: Estimated volunteer performance - This is either set arbitrarily or
                might be based upon judicious assesment of cohort-wide volunteer performance
                on a similar analysis task. It is required to initialize the likelihood
                formulation framework for each volunteer's agent.
        """

        # assign class variables from args
        self.p0 = p0  # prior probability real
        self.epsilon = epsilon  # estimated volunteer performance

        # dictionaries to save user / subject probabilities
        self.users = dict()
        self.subjects = dict()

        # Directive to update - if True, then a volunteer agent's posterior probability of
        # containing an interesting object will be updated whenever an expertly classified
        # "gold standard" subject is classified by that volunteer.
        self.gold_updates = True


    # update User Data (classification history and probabilities)
    def updateUserData(self,cl):
        """ Update User Data with respect to classifications

        Parameter:
        -----------
        cl: dict
            Contains all information for a classification

        """

        # ##Michael @Marco
        # This looks like it will get pretty complicated pretty quickly.
        # What if we create another module, similar to agent in the original
        # swap code, then create a dictionary of agents?
        #
        # Then you could initialize the probability_history and probability_current
        # fields when the object is created


        # check if user is new and create in user dictionary if not
        if cl['user_name'] not in self.users:
            self.users[cl['user_name']] = {
                      'annotations':[],
                      'gold_labels':[],
                      'labels':dict(),
                      'probability_history':dict(),
                      'n_classified':0,
                      'probability_current':dict()}

        # update label data
        current_user = self.users[cl['user_name']]
        current_user['annotations'].append(cl['annotation'])
        current_user['gold_labels'].append(cl['gold_label'])
        current_user['n_classified'] += 1

        # check if gold label exists and create if not
        if not cl['gold_label'] in current_user['probability_current']:
            current_user['probability_history'][cl['gold_label']] = []
            current_user['probability_current'][cl['gold_label']] = self.epsilon
            current_user['labels'][cl['gold_label']] = {'n':0,'n_match':0}

        # check if annotation label exists and create if not
        if not cl['annotation'] in current_user['probability_current']:
            current_user['probability_history'][cl['annotation']] = []
            current_user['probability_current'][cl['annotation']] = self.epsilon
            current_user['labels'][cl['annotation']] = {'n':0,'n_match':0}

        # update number of subjects of that label seen by user
        current_user['labels'][cl['gold_label']]['n'] += 1

        # update number of matches of that label seen by user
        if cl['gold_label'] == cl['annotation']:
            current_user['labels'][cl['gold_label']]['n_match'] += 1

        # update user probability
        n_classified_of_that_label = current_user['labels'][cl['gold_label']]['n']
        n_correctly_classified = current_user['labels'][cl['gold_label']]['n_match']
        p_classified_correctly = n_correctly_classified / n_classified_of_that_label

        # save updated probability
        current_user['probability_history'][cl['gold_label']].append(p_classified_correctly)
        current_user['probability_current'][cl['gold_label']] = p_classified_correctly



    def getUserData(self):
        return self.users

    # update subject probability
    def updateSubjectData(self, cl):
        # check if subject is new and create in user dictionary if yes
        if cl['subject_id'] not in self.subjects:
            current_subject = {'gold_label': cl['gold_label'],
                               'annotation_history': [],
                               'user_probabilities': [],
                               'probability_labels': {'1': self.p0,
                                                      '0': 1-self.p0},
                               'current_label': '',
                               'current_max_prob': self.p0,
                               'max_prob_history': [self.p0]}

            self.subjects[cl['subject_id']] = current_subject


        # get current user data
        current_user = self.users[cl['user_name']]

        # update current annotation
        current_subject= self.subjects[cl['subject_id']]
        current_subject['annotation_history'].append(cl['annotation'])
        # TODO: if user does not exist there us no current_user (if user has no gold label classification)
        current_subject['user_probabilities'].append(current_user['probability_current'][cl['annotation']])

        # add current probability to class label
        #user_prob = current_user['probability_current'][cl['annotation']]

        # update success probability
        # TODO: get rid of hard-coded annotation labels
        if '1' in current_user['probability_current']:
            user_pos = float(current_user['probability_current']['1'])
        else:
            user_pos = self.epsilon
        if '0' in current_user['probability_current']:
            user_fail = current_user['probability_current']['0']
        else:
            user_fail = self.epsilon

        # get current subject probability
        sub_pos = current_subject['current_max_prob']

        # calculate subject probability times current user confidence in
        # positive labels
        sub_times_user = float(sub_pos) * float(user_pos)

        # TODO: change hard-coded annotation labels
        # if positive annotation
        if cl['annotation'] == '1':
            sub_pos_new = sub_times_user / \
                          (sub_times_user + (1-user_fail) * (1-sub_pos))
        # if negative annotation
        elif cl['annotation'] == '0':
            sub_pos_new = (sub_pos * (1-user_pos)) / \
                          (sub_pos * (1-user_pos) + (user_fail * (1-sub_pos)))

        current_subject['probability_labels']['1'] = sub_pos_new
        current_subject['current_max_prob'] = sub_pos_new
        current_subject['current_label'] = '1' if sub_pos_new > 0.5 else '0'
        current_subject['max_prob_history'].append(sub_pos_new)

    def getSubjectData(self):
        return self.subjects

    # Process a classification
    def processOneClassification(self, cl):
        # if subject is gold standard and gold_updates are specified,
        # update user success probability
        if ((cl['gold_label'] in ('0', '1')) and self.gold_updates):
                self.updateUserData(cl)
                # update Subject probability
                self.updateSubjectData(cl)


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
        self.users = Bureau(User)
        self.subjects = Bureau(Subject)

        # Directive to update - if True, then a volunteer agent's posterior
        # probability of containing an interesting object will be updated
        # whenever an expertly classified "gold standard" subject is
        # classified by that volunteer.
        self.gold_updates = True

    def updateUserData(self, cl):
        """ Update User Data - Process current classification """

        # Get user agent from bureau or create a new one
        user = self.getUserAgent(cl['user_name'])
        user.addClassification(cl)

    def getUserData(self):
        return self.users

    def updateSubjectData(self, cl):
        """ Update Subject Data - Process current classification """

        # check if agent is in bureau and create new one if not
        subject = self.getSubjectAgent(cl['subject_id'])
        user = self.getUserAgent(cl['user_name'])

        # process classification
        subject.addClassification(cl, user)

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

    def getUserAgent(self, agent_id):
        if self.users.has(agent_id):
            return self.users.getAgent(agent_id)
        else:
            agent = User(agent_id, self.epsilon)
            self.users.addAgent(agent)
            return agent

    def getSubjectAgent(self, agent_id):
        if self.subjects.has(agent_id):
            return self.subjects.getAgent(agent_id)
        else:
            agent = Subject(agent_id, self.p0)
            self.subjects.addAgent(agent)
            return agent
