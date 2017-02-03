################################################################
# SWAP implementation for matlab files

from .swap import SWAP

import sys
import _pickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

class MATSWAP(SWAP):

    """ Create MATSWAP object which implements SWAP based on .MAT file input

    Parameters
    -----------
    dotMatFile: str
        A .MAT file that can be loaded with scipy.io.loadmat and contains a dictionary with arrays for the
        different variables:
        - annotation (the label submitted by the volunteer)
        - classification_id (autoincremented unique id for each classification)
        - diff (the name of the individual difference image for a specific subject)
        - gold_label (the "expert" provided label taken to be the ground truth label. Ignore
                      classifications with a gold_label = -1)
        - machine_score (CNN score for this object)
        - object_id (PS1 TSS unique object id.  There are multiple subjects per object)
        - subject_id (autoincremented unique subject id)
        - user_id (autoincremented unique id for volunteers.  This field is blank if the
                   volunteer is not looged in when submitting a classification)
        - user_name (volunteers username)

    p0: numeric
        prior probability of a subject to be of interest
    epsilon:numeric
        prior probability for a user to correctly classify a subject

    """

    def __init__(self, dotMatFile, p0=0.01, epsilon=0.5):
        self.data = sio.loadmat(dotMatFile)
        self.subjects = np.squeeze(self.data["subject_id"])
        self.usernames = np.squeeze(self.data["user_name"])
        self.annotations = np.squeeze(self.data["annotation"])
        self.gold_labels = np.squeeze(self.data["gold_label"])
        self.classifications = np.squeeze(self.data["classification_id"])
        self.p0 = p0  # prior probability real
        self.epsilon = epsilon  # estimated volunteer performance
        self.value_to_label = ["No", "Yes"]
        self.gold_updates = True

        self.M, self.unique_users = self.initialiseM()
        self.S = self.initializeS()

        self.dt = np.zeros(self.M.shape)
        self.dt_prime = np.zeros(self.M.shape)
        self.user_history = {}
        self.subject_history = {}

    def initialiseM(self):
        """ Initialize user confusion matrix with prior probabilites of users

        Returns
        -------
            (np.array,np.array) :
                2D array with dimensions number of distinct users * 2, all values initialized to epsilon
                1D array with unique users

        """

        unique_users = np.unique(self.data["user_name"])
        return np.ones((len(unique_users), 2)) * self.epsilon, unique_users

    def process(self):
        """ Process classifications and update subject and user data


        Updates user confusion matrix given the true label &
        updates subjects' probability of being of interest, given historical classifications,
        the users' annotation and the users' estimated accuracy

        """
        total = len(self.classifications)
        print(total)
        # for each classification
        for i, classification_id in enumerate(self.classifications):
            # select current subject
            subject_id = self.subjects[i]
            # find user index in unique user array
            user_index = self.unique_users.tolist().index(self.usernames[i])
            # find index of first occurrence of current subject in classifications
            subject_index = int(np.where(np.array(self.subjects) == subject_id)[0][0])
            # get user and gold label
            annotation = self.annotations[i]
            gold, label = self.isGoldStandard(i)
            # if subject is gold standard update user success probability
            if gold and self.gold_updates:
                # update user success probabilities for given label
                self.updateM(user_index, label, annotation)
            # given the user annotated as 1
            if annotation == 1:
                # update probability that subject is of interest (=1), given the users accuracy
                self.S[subject_index] = self.S[subject_index] * self.M[user_index][1] / \
                    (self.S[subject_index] * self.M[user_index][1] +
                     (1 - self.M[user_index][0]) * (1 - self.S[subject_index]))
            elif annotation == 0:
                # update probability that subject is not of interest (=0), given the users accuracy
                self.S[subject_index] = self.S[subject_index] * (1 - self.M[user_index][1]) / \
                    (self.S[subject_index] * (1 - self.M[user_index][1]) +
                     (self.M[user_index][0]) * (1 - self.S[subject_index]))
            # fill invalid? fields with prior
            np.ma.fix_invalid(self.S, copy=False, fill_value=self.p0)
            # update subjects probability of being of interest
            try:
                self.subject_history[subject_id].append(self.S[subject_index])
            except KeyError:
                self.subject_history[subject_id] = [self.p0, self.S[subject_index]]
            sys.stdout.write("%.3f%% complete.\r" % (100 * float(i) / float(total)))
            sys.stdout.flush()

    def isGoldStandard(self, i):
        """ Return if current classification is of a subject with a gold label and return the label """
        try:
            label = self.gold_labels[i]
            if label == -1:
                raise ValueError
        except:
            return False, None
        if label is not None:
            return True, label