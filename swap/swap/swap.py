################################################################
# SWAP implementation
# 

#import modules
import _pickle as pickle
import scipy.io as sio
import swap.Server


# read classifications
def test_swap():
    n_classifications=1000
    max_batch_size = 1000
    server = swap.Server(.5,.5)
    # initialize curser with limit and max batch size
    classification_cursor = server.classifications.find().limit(n_classifications).batch_size(min(max_batch_size,n_classifications))
    swappy = SWAP()
    # loop over cursor to retrieve classifications
    for i in range(0,8):
        current_classification = classification_cursor.next()
        swappy.processOneClassification(current_classification)
    swappy.getUserData()
    
    

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
    def updateSubjectData(self,cl):
        # check if subject is new and create in user dictionary if yes
        if cl['subject_id'] not in self.subjects:
            self.subjects[cl['subject_id']] = {
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
                    
           
        
    # Process a classification
    def processOneClassification(self,cl):
        # if subject is gold standard update user success probability
        if cl['gold_label'] in ('0','1'):
                self.updateUserData(cl)               
        # update subject probability              
#        if cl['annotation'] == '1':
#            # update probability that subject is of interest (=1), given the users accuracy
#            self.S[subject_index] = self.S[subject_index] * self.M[user_index][1] / \
#                (self.S[subject_index] * self.M[user_index][1] +
#                 (1 - self.M[user_index][0]) * (1 - self.S[subject_index]))
#        elif cl['annotation']== '0':
#            # update probability that subject is not of interest (=0), given the users accuracy
#            self.S[subject_index] = self.S[subject_index] * (1 - self.M[user_index][1]) / \
#                (self.S[subject_index] * (1 - self.M[user_index][1]) +
#                 (self.M[user_index][0]) * (1 - self.S[subject_index]))
    

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









