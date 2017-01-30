#!/usr/bin/python3

import sys
import _pickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

from pymongo import MongoClient


class SWAP(object):
    """
        SWAP implementation, which calculates and updates a confusion matrix for each user
        as well as the probability that a particular subject contains an object of interest.

        See: Marshall et al. 2016: "Space Warps I: Crowd-sourcing the Discovery of
        Gravitational Lenses", MNRAS, 455, 1171 (hereafter Marshall et al. 2016) for
        algorithm explanation.
    """

    def __init__(self, db, subjects, p0=0.01, epsilon=0.5):
        """
            Initialize SWAP instance
            Args:
                db: (pymongo database) Reference to the MongoClient database
                subjects: (list) List of subject id numbers. Are the values distinct?
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
        self.db = db
        self.p0 = p0  # prior probability real
        self.epsilon = epsilon  # estimated volunteer performance

        # define value to label map - This simply maps the list indices [0, 1],
        # which can also be interpreted as Boolean values, to human-readable
        # strings ["No", "Yes"]
        self.value_to_label = ["No", "Yes"]

        # Directive to update - if True, then a volunteer agent's posterior probability of
        # containing an interesting object will be updated whenever an expertly classified
        # "gold standard" subject is classified by that volunteer.
        self.gold_updates = True

        """
            self.subjects:
                Array containing data on each subject - Seems to currently be a list of
                subject IDs.

                In principle (in addition to data that are required
                by the classification interface to render the classification task) each subject
                may be annotated with additional metadata e.g. whether the subject is an
                expertly classified"gold standard" subject.

                It seems that these data are retrieved from a mongo database using the
                subject ID as a search parameter.

            self.S:
                Array containing the probability score (the probability that a subject contains an
                object of interest) assigned to each subject.

            NOTE: Just like my (michael) comments below about M and unique_users,
            this doesn't seem like a good way of doing this
        """
        self.subjects = subjects
        self.S = self.initializeS()

        """
            self.unique_users:
                A list of all users that contributed classifications
            self.M:
                2d array, where each row is a user's confusion matrix.
                The matrices of each user appear in the same order
                as in unique_users.

                Note that the normalization criterion for the elements of the
                nominally 2x2 confusion matrix specified immediately following
                equation 3 of Marshall et al. 2016 renders the off-diagonal elements
                redundant. Accordingly only elements on the leading diagonal of
                the confusion matrix are computed and stored.

            NOTE: This doesn't seem like a good implementation.
            Would it make more sense to have a list of dicts, where
            each item in the list contains the username, user_id,
            matrix, etc. of each user?
        """
        # restructured class assignments for clarity
        initM = self.initializeM()
        self.M = initM[0]
        self.unique_users = initM[1]

        """
            self.dt:
                Required for computation that updates a user's confusion matrix following classifiaction of a
                gold standard subject. According to Marshall et al. 2016:
                "dt stands for all N_LENS + N_NOT training data that the agent has heard about to date."
                In other words simply the total number of classifications of gold standard subjects the user
                performed so far.
            self.dt_prime:
                Required for computation that updates a user's confusion matrix following classifiaction of a
                gold standard subject. Unlike, dt, dt_prime is only incremented when a user correctly classifies
                a gold standard subject. In other words it is the sum of all boring (gold standard) subjects correctly
                classified as boring plus the sum of all interesting (gold standard) correctly classified as
                interesting.
        """
        self.dt = np.zeros(self.M.shape)
        self.dt_prime = np.zeros(self.M.shape)

        """
            self.user_history:
                QBECK
            self.subject_history:
                QBECK
        """
        self.user_history = {}
        self.subject_history = {}

    def setGoldUpdates(self, str):
        """
            QBECK
        """
        if str == "on":
            self.gold_updates = True
        elif str == "off":
            self.gold_updates = False
        else:
            raise ValueError

    def initializeM(self):
        """
           Initialises a matrix with each row being a
           compressed confusion matrix for each unique
           username in the database. Assigns all classifications
           to a single agent when not logged in.

            Returns: (np.array, list)
                1. Array with 2 columns and as many rows as users
                   I'm guessing this is a performance matrix for each user?
                2. List of users
        """

        # gets a list of all uses from the db
        unique_users = self.db["classifications"].distinct("user_name")

        # creates a matrix with two columns and as many rows as users
        # The columns represent:
        # 0: the probability that the user will correctly identify a subject containing
        #    an object of interest (interesting | interesting).
        # 1: the probability that the user will correctly recognize that a subject
        #    does not contain an object of interest (boring | boring)
        matrix = np.ones((len(unique_users), 2)) * self.epsilon  # initially assign equal probability epsilon to both cases.

        return (matrix, unique_users)

    def initializeS(self):
        """
            Initialize the probability matrix for each subject
            Returns: (np.array) List with the initial probability value in p0
        """
        return np.ones((np.shape(self.subjects))) * self.p0

    def process(self):
        """
            Process the classifications in the database. Each classification includes
            data pertaining to the subject being classified and the agent of the volunteer
            who performed the classification.
        """

        # Retrieve all the classifications from a mongodb database
        cursor = self.db["classifications"].find()

        # utility working variables
        total = cursor.count()
        skipped_count = 0
        count = 1

        # loop over classifications
        for doc in cursor:
            # retrieve the subject id that will be used to index various lists containing
            # current probabilities that a subject contains an object of interest as well
            # as intermediate quantities that are required to compute those probabilities.
            subject_id = int(doc["subject_id"])

            # The list self.subjects is initialized using the contents of a constructor argument
            # and can apparently be used to filter subjects that are stored in the database if the
            # corresponding subject_id is omitted from that list.
            if subject_id in set(self.subjects):

                # define an integral user_index that corresponds to the position at which
                # the user_name retrieved from the database for the current classification
                # is listed in the unique_users list. This index will be used to index various
                # lists containing current confusion matrices that a subject contains an object
                # of interest as well as intermediate quantities that are required to compute
                # those probabilities.
                user_index = self.unique_users.index(doc["user_name"])
                # perform a similar action for the subjects list.
                subject_index = int(np.where(np.array(self.subjects) == subject_id)[0][0])

                # determine whether the classification identified an object of interest or not
                annotation = self.value_to_label.index(doc["annotations"][0]["value"])
                # Apparently, gold standard classification data are stored in a separate collection
                # and each subject_id must be checked in order to determine whether is corresponds
                # to a gold-standard subject.
                gold, label = self.isGoldStandard(subject_id)

                # If the metadata for the current subject indicates that  is is an expertly
                # classified "gold standard" subject, and the gold_updates is true (always the
                # case as this is hard coded in the constructor!), then apply equation 5 from
                # Marshall et al. 2016 to appropriately update the confusion matrix of the current
                # user.
                if gold and self.gold_updates:
                    self.updateM(user_index, label, annotation)

                # See subject probability update rules from Marshall et al. 2016 (Eqn. 10)
                if annotation == 1:
                    self.S[subject_index] = self.S[subject_index] * self.M[user_index][1] / \
                        (self.S[subject_index] * self.M[user_index][1] +
                         (1 - self.M[user_index][0]) * (1 - self.S[subject_index]))
                elif annotation == 0:
                    self.S[subject_index] = self.S[subject_index] * (1 - self.M[user_index][1]) / \
                        (self.S[subject_index] * (1 - self.M[user_index][1]) +
                         (self.M[user_index][0]) * (1 - self.S[subject_index]))

                # NOTE if we do switch away from the indexed array system,
                # then might have to check calculations for div0 and Inf

                # Fixes replaces invalid data (/0, Inf) with p0
                np.ma.fix_invalid(self.S, copy=False, fill_value=self.p0)

                try:
                    # tries to append the current probability to the subject's history
                    self.subject_history[subject_id].append(self.S[subject_index])
                except KeyError:
                    # otherwise initializes a history list for this subject
                    # in subject_history with p0s
                    self.subject_history[subject_id] = [self.p0, self.S[subject_index]]

                # Print progress to stdout
                sys.stdout.write("%.3f%% complete.\r" %
                                 (100 * float(count) / float(total - skipped_count)))
                sys.stdout.flush()
                # Increment this counter for every subject classification that was successfully
                # processed.
                count += 1

            # Increment this counter if a subject was present in the classification database
            # but was not included in the list of subjects to be processes that was passed
            # as a constructor argument.
            skipped_count += 1

    def isGoldStandard(self, subject_id):
        """
        Gold standard classification data are stored in a separate collection
        and each subject_id must be checked in order to determine whether is corresponds
        to a gold-standard subject.
        """
        diff_id = self.db["diffID_to_subjectID"].\
            find({"subject_id": {"$eq": subject_id}})[0]["diff_id"]

        try:
            label = self.db["gold_standard"].\
                find({"id": {"$eq": diff_id.split("_")[0]}})[0]["label"]

            if label == -1:
                raise ValueError
        except:
            return False, None
        if label is not None:
            return True, label

    def updateM(self, user_index, label, annotation):
        """
        Updates the confusion matrix of a volunteer's agent following classification
        of a gold standard subject.
        """
        # Increment the user's count of classified gold standard subjects
        self.dt[user_index, label] += 1
        if annotation == label:
            # Increment the user's count of CORRECTLY classified gold standard subjects
            self.dt_prime[user_index, label] += 1
        # Update the user's confusion matrix according to equation 2 of Marshall et al. 2016
        self.M[user_index, label] = np.divide(
            self.dt_prime[user_index, label], self.dt[user_index, label])

        # Maintain a running history of the eveolution of a user's confusion matrix
        try:
            self.user_history[self.unique_users[user_index]]
        except KeyError:
            # QBECK why does this use integers as dictionary keys
            self.user_history[self.unique_users[user_index]] = {0: [], 1: []}
        self.user_history[self.unique_users[user_index]][label].append(self.M[user_index, label])
        np.ma.fix_invalid(self.M, copy=False, fill_value=self.epsilon)

    def save(self, filename):
        """
            Save the processed data to pickled mat files. Creates two
            files, one for the user_history and one for the subject_history

            Args:
                filename (str):
                    filename suffix to store the data in. replaces the extension with .pkl
                    ex. 'foo.mat' will create 'user_dict_foo.pkl' and 'subject_dict_foo.pkl'
        """
        sio.savemat(filename, {"subjects": self.subjects,
                               "p0": self.p0,
                               "epsilon": self.epsilon,
                               "unique_users": self.unique_users,
                               "M": self.M,
                               "S": self.S,
                               "dt": self.dt,
                               "dt_prime": self.dt_prime})
        # FIXME: this won't work with paths, only with filenames
        out = open("user_dict_" + filename[:-4] + ".pkl", "wb")
        pickle.dump(self.user_history, out)
        out.close()

        out = open("subject_dict_" + filename[:-4] + ".pkl", "wb")
        pickle.dump(self.subject_history, out)
        out.close()









