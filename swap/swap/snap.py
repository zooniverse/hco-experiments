#!/usr/bin/python3

from .swap import SWAP

import sys
import _pickle as pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio

class SNAP(SWAP):

    def __init__(self, db, subjects, p0=0.01, epsilon=0.5, n=100):
        self.n = n
        step = 1 / float(n)
        self.thresholds = np.arange(0, 1 + step, step)
        SWAP.__init__(self, db, subjects, p0=0.01, epsilon=0.5)

    def initialiseM(self):
        """
           Initialises a matrix with each row being a compressed confusion matrix for
           each unique user name in the database.  The method assigns all not logged in
           classifications to a single agent.
        """
        # unique_users = self.db["classifications"].distinct("user_name")

        # return np.ones((len(unique_users)+1,2))*self.epsilon, unique_users+["ps13pi_robot"]

        unique_users = ["robot_" + str(x) for x in range(1, (self.n) + 1, 1)]
        return np.ones((self.n, 2)) * self.epsilon, unique_users

    def get_robot_annotation(self, user_index, id):
        machine_score = self.db["machine_classifications"].find({"id": id})[0]["confidence_factor"]
        threshold = self.thresholds[user_index]
        return machine_score > threshold

    def process(self):
        count = 1
        for subject_id in self.subjects:
            subject_index = int(np.where(np.array(self.subjects) == subject_id)[0][0])
            id = self.db["diffID_to_subjectID"].find({"subject_id": subject_id})[0]["id"]
            gold, label = self.isGoldStandard(subject_id)
            for user_name in self.unique_users:
                user_index = self.unique_users.index(user_name)
                annotation = self.get_robot_annotation(user_index, id)

                if gold:
                    self.updateM(user_index, label, annotation)
                else:
                    continue
                if annotation == 1:
                    self.S[subject_index] = self.S[subject_index] * self.M[user_index][1] / \
                        (self.S[subject_index] * self.M[user_index][1] +
                         (1 - self.M[user_index][0]) * (1 - self.S[subject_index]))
                elif annotation == 0:
                    self.S[subject_index] = self.S[subject_index] * (1 - self.M[user_index][1]) / \
                        (self.S[subject_index] * (1 - self.M[user_index][1]) +
                         (self.M[user_index][0]) * (1 - self.S[subject_index]))
                np.ma.fix_invalid(self.S, copy=False, fill_value=self.p0)
                try:
                    self.subject_history[subject_id].append(self.S[subject_index])
                except KeyError:
                    self.subject_history[subject_id] = [self.p0, self.S[subject_index]]

                # sys.stdout.write("%.3f%% complete.\r" % (100*float(count)/float(total)))
                # sys.stdout.flush()
                # count += 1

    """
    def updateM(self,user_index, label, annotation):
        self.dt[user_index,label] += 1
        if annotation == label:
            self.dt_prime[user_index,label] += 1
        #print self.calculateAlpha(user_index, label)
        self.M[user_index,label] = self.calculateAlpha(user_index, label)
        try:
            self.user_history[self.unique_users[user_index]]
        except KeyError:
            self.user_history[self.unique_users[user_index]] = {0:[],1:[]}
        self.user_history[self.unique_users[user_index]][label].append([self.calculateAlpha(user_index, label)])
        #np.ma.fix_invalid(self.M,copy=False,fill_value=self.epsilon)

    def calculateAlpha(self, user_index, label):
        if self.dt[user_index,label] <= self.m:
            return self.M[user_index,label]
        if self.dt[user_index,label] / self.n >= 1:
            return np.divide(self.dt_prime[user_index,label], self.dt[user_index,label])
        return self.epsilon + (self.dt[user_index,label] / self.n)*(np.divide(self.dt_prime[user_index,label], self.dt[user_index,label]) -self.epsilon)
    """
    """
    def save(self, filename):
        sio.savemat(filename,{"subjects":self.subjects, \
                            "p0":self.p0, \
                            "epsilon":self.epsilon, \
                            "unique_users":self.unique_users, \
                            "M":self.M, \
                            "S":self.S, \
                            "dt":self.dt, \
                            "dt_prime":self.dt_prime,
                            "m":self.m,\
                            "n":self.n}
              )
        out = open("user_dict_"+filename.strip(".mat")+".pkl","wb")
        pickle.dump(self.user_history,out)
        out.close()
     """