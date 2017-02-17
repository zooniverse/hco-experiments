################################################################
# SWAP implementation
# - new version to work with agent / bureau classes
# 

from swap.agents.bureau import Bureau
from swap.agents.subject import Subject
from swap.agents.user import User

class SWAP_AGENTS(object):
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
        
        # initialize bureaus to manage user / subject agents
        self.user_bureau = Bureau('users')
        self.subject_bureau = Bureau('subjects')

        # Directive to update - if True, then a volunteer agent's posterior probability of
        # containing an interesting object will be updated whenever an expertly classified
        # "gold standard" subject is classified by that volunteer.
        self.gold_updates = True
        
        
    def updateUserData(self,cl):
        """ Update User Data - Process current classification """
        # check if agent is in bureau and create new one if not
        if not self.user_bureau.isAgentInBureau(cl['user_name']):
            # create new user agent and add to bureau
            current_user = User(cl['user_name'],self.epsilon)
            self.user_bureau.addAgent(current_user)
        else:
            current_user = self.user_bureau.getAgent(cl['user_name'])
        # process classification
        current_user.addClassification(cl)
                
    
    def getUserData(self):
        return self.user_bureau
    
    def updateSubjectData(self,cl):
        """ Update Subject Data - Process current classification """
        # check if agent is in bureau and create new one if not
        if not self.subject_bureau.isAgentInBureau(cl['subject_id']):
            # create new subject agent and add to bureau
            current_subject = Subject(cl['subject_id'],self.p0)
            self.subject_bureau.addAgent(current_subject )
        else:
            current_subject = self.subject_bureau.getAgent(cl['subject_id'])
        # process classification
        current_subject.addClassification(cl)
        
    
    def getSubjectData(self):
        return self.subject_bureau                         
        
    # Process a classification
    def processOneClassification(self,cl):
        # if subject is gold standard and gold_updates are specified, 
        # update user success probability
        if ((cl['gold_label'] in ('0','1')) and self.gold_updates):
                self.updateUserData(cl) 
                # update Subject probability
                self.updateSubjectData(cl)





if __name__ == "__main__":
    from swap import Server
    import time          

    def test_swap():
        start = time.time()
        server = Server(.5,.5)
        max_batch_size = 1e5
        
        # get classifications
        classifications = server.getClassifications()
        
        n_classifications= 1e6
        
        # determine and set max batch size
        classifications.batch_size(int(min(max_batch_size,n_classifications)))
        
        swap = SWAP_AGENTS()
        
        # loop over classification curser to process 
        # classifications one at a time
        print("Start: SWAP Processing " + str(n_classifications) + " classifications")
        for i in range(0,n_classifications):
            # read next classification
            current_classification = classifications.next()
            # process classification in swap
            swap.processOneClassification(current_classification)
            if i % 100e3 ==0:
                print("   " + str(i) + "/" + str(n_classifications))
        print("Finished: SWAP Processing " + str(i) + "/" + str(n_classifications) + " classifications")
        
        
        
        
        
        server.process()
        print("--- %s seconds ---" % (time.time() - start))
        swappy = server.getSWAP()
        ud = swappy.getUserData()
        sd = swappy.getSubjectData()
        
    test_swap()


