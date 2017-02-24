#!/usr/bin/python

import sys # for Capturing
import numpy as np
from cStringIO import StringIO # for Capturing
"""
    
    Capturing:         goto-line 21
    NeuralNet:         goto-line 42
    NeuralNetPerform:  goto-line 580
    Autoencoder:       goto-line 686
    SparseAutoencoder: goto-line 774
    LinearDecoder:     goto-line 862
    SoftMaxClassifier: goto-line 942
    DeepNerualNet:     goto-line 1054
    
"""

np.seterr(all="raise")

iteration = 0
iters = []
costs = []
class Capturing(list):
    """
        Taken from:
        http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
        
        this is a context manager for capturing print statements as elements of a list.
        
        Usage:
        
        with Capturing() as output:
            do_something(my_object)
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

class NeuralNet(object):
    
    """
        object: NeuralNet
        superclass: object
        
    """
    
    def __init__(self, input, targets, architecture={}, LAMBDA=0.0, classify=False, maxiter=100, saveFile=None):
        """
            Initialise the data attributes of the NeuralNet object.
            
            parameters:
            
                input: <numpy array> containing the training data with dimensions
                       nxm, where n is the number of features and m is the number 
                       of training examples.  The bias unit should not be added 
                       to the input data array before instantiating the NeuralNet.
                       The bias is automatically added to the input array.

                targets: <numpy array> containing the targets for each training example. 
                         k x m matrix, where k is the number of target values per training
                         example.
            
                architecture: <dict> containing the a key-value pair for each hidden 
                              layer of the NerualNet.  Where the keys are integer values
                              corresponding to the index of the hidden layer starting from 1
                              e.g. for the first hidden layer the key is 1.  The values are
                              positive integers defining the number of hidden units per hidden
                              layer, e.g. 200.  architecture should therefore take the form
                              {1:200} for a NeuralNet with 1 hidden layer with 200 logistic units.
            
                LAMBDA: positive <float> regularising constant.  Determines the degree to which
                        regularisation is applied.  The larger the value the greater 
                        effect of the regularisation term on the cost function.
            
                classify: <boolean> flag denoting whether this is a classification problem or not.
                          True if it is classification, False otherwise.  If True the targets will
                          be mapped using the indicator function.
            
                maxiter: positive <int> maximum number of iterations. Passed to scipy.optimize
                         functions.
            
                saveFile: <.mat file> containing the _hiddensize, _LAMBDA, and _trainedParams
                          from a previously trained NeuralNet object.
            
            returns:
            
                None
                
        """        
        import types
        # Do some checking of the user input 
        # do some checking on the architecture passed in
        # check that the architecture is a dictionary.
        assert type(architecture) is types.DictType, \
               "<architecture> must be a dict (e.g. {1:200}): %r is not valid\n" % architecture
        # loop through keys and values to check type and parity
        for key in architecture.keys():
            # check keys are positive integers
            assert type(key) is types.IntType, \
                   "<architecture> keys must be integers: %r is not a valid key" % key
            assert key > 0, \
                   "<architecture> keys must be positive integers: %r is not valid key\n" % key
            # check values are positive integers
            assert type(architecture[key]) is types.IntType, \
                   "<architecture> keys must be integers: %r is not a valid key" % architecture[key]
            assert architecture[key] > 0, \
                   "<architecture> keys must be positive integers: %r is not valid key\n" % architecture[key]
        # check LAMBDA is a positive number, it is cast as float when initiated, see def. of self._LAMBDA
        assert LAMBDA >= 0, \
               "<LAMBDA> must be a positive number: %r is not valid\n" % LAMBDA
        # check classify is a boolean
        assert type(classify) is types.BooleanType, \
               "<classify> must be a boolean: %r is not valid\n" % classify
        # check maxiter is a positive integer
        assert type(maxiter) is types.IntType, \
               "<maxiter> must be an integer: %r is not valid\n" % maxiter
        assert maxiter > 0, \
               "<maxiter> must be a positive integer: %r is not valid\n" % maxiter  
        # intialise the data attributes of the NeuralNet
        # add bias unit to input
        self._input = np.concatenate((np.ones(np.shape(input)[1])[np.newaxis], input), axis=0) # (n+1)xm
        self._targets = targets # 1xm
        self._maxiter = maxiter
        self._classify = classify
        # if this is a classification problem then comput the indicator function here this saves
        # overhead on calculating this each time self.costFunction is called.
        if self._classify == True and len(np.unique(self._targets)) > 2:
            self._indicatorFunction = self.labelsToIndicatorFunction(self._targets) # kxm
        # check if a saved network has been selected
        if saveFile == None:
            # if there is no saveFile initialise the data attributes 
            # of the NeuralNet from those given when the Neural Net 
            # instance is created.
            self._architecture = architecture
            # add the number of input units to the architecture not including the bias unit
            self._architecture[0] = np.shape(self._input)[0] - 1
            # add the number of output units to the architecture
            if self._classify == True and len(np.unique(self._targets)) > 2:
                # if classification problem and more than 2 classes the number of output nodes
                # is equal to the number of unique labels
                self._architecture[len(self._architecture.keys())] = len(np.unique(self._targets))
            elif self._classify == True and len(np.unique(self._targets)) == 2:
                # else if binary classification use one output node
                self._architecture[len(self._architecture.keys())] = 1
            elif self._classify == False:
                # else we have a regression problem and the number of output nodes is equal to the
                # number of target values per example
                self._architecture[len(self._architecture.keys())] = np.shape(self._targets)[0]
            self._LAMBDA = float(LAMBDA)
            # if there is no saveFile initialise the trainied params as 
            # None.  This will be used to store parameters once network has
            # been trained.
            self._trainedParams = None
        else:
            # import here to avoid overhead if no saveFile is given.
            import scipy.io as sio
            # try to open the given saveFile
            try:
                savedNeuralNetSetup = sio.loadmat(saveFile)
                # initialise data attributes as saved in saveFile
                self._architecture = {}
                self._LAMBDA = float(savedNeuralNetSetup["LAMBDA"])
                # was having problems with loading this array from saved networks created by different versions of python.
                # I think is is beacuse newer versions of sio.loadmat save the array in a different order to previous versions
                # i.e. either column of row major not sure which but when I do sio.savemat in python 2.6 I get a FutureWarning.
                # Solution seems to be to squeeze the loaded array to remove the redundant dimension.
                self._trainedParams = np.squeeze(savedNeuralNetSetup["trainedParams"])
                # loop through all keys insaved network setup
                for key in savedNeuralNetSetup.keys():
                    # if the key continas the specified string...
                    if "architecture" in key:
                        # ...remove the string from the key name and cast it as an int
                        # this gives a key in the format for the self._architecture dict.
                        layerKey = int(key.replace("architecture", ""))
                        # add each key value pair to the dictionary.
                        self._architecture[layerKey] = savedNeuralNetSetup[key]
            # catch the error if saveFile can't be opened and advise user.
            except IOError:
                print saveFile
                print "Saved neural network file not found!"
                print "Is the file in the current path?"

    def search(self):
        
        """
            Useful search method, handy way of doing type searching on user defined classes.
            
            parameters:
            
                None
            
            returns:
            
                A string matching the name of the user defined class
            
        """
        return "NeuralNet"
    
    def randInitialiseWeights(self, nIn, nOut):
        """
            Randomly (for symmetry breaking) initialize the weights of a layer with nIn 
            incoming connections and nOut outgoing connections.
            
            We choose weights uniformly from the interval [-r, r]
            
            parameters:
            
                nIn: <int> number of units in the previous layer, not including the bias unit.
            
                nOut: <int> number of units in the next layer.
            
            returns:
            
                <numpy-array> of randomly initiaised weights of size nOut x nIn 
        """
        # Note: The first row corresponds to the parameters for the bias units
        r = np.sqrt(6) / (np.sqrt(nOut + nIn + 1))
        return np.random.rand(nOut, (nIn + 1)) * 2 * r - r

    def initialise(self):
        """
            Randomly intialise the weights for the entire NeuralNet.  Calls self.randInitialiseWeights
            to get random weights for each layer, then unravels these weights into a single vector.  The
            vector form is required in order to pass the network weights to the scipy optimisation function.
            
            parameters:
            
                None
            
            returns:
            
                intialParams: <numpy-array> vector containg randomly intialised weights for all
                              layers of the NerualNet.
        """
        
        # initialise initialParams by initialising the weights for the connection between the input and 
        # first hidden layer.
        initialParams = np.ravel(self.randInitialiseWeights(self._architecture[0], \
                                                           self._architecture[1]), order="F")
        # loop through the remaining layers and intialise the weights
        for layer in self._architecture.keys()[1:-1]:
            initialParams = np.concatenate((initialParams, \
                                           np.ravel(self.randInitialiseWeights(self._architecture[layer], \
                                                                               self._architecture[layer+1]), \
                                                    order="F")), \
                                          axis=0)
        return initialParams

    def reshapeParams(self, params):
        """
            Reshape a vector of the weights of the network into matrices
            
            parameters:
            
                params: <numpy-array> vector of weight for all connections of the network.
            
            returns:
            
                thetas: <dict> a dictionary contining the theta matrices corresponding to the
                        connections between each layer of the network.  The keys correspond to
                        the layer to which the set of weights map the input.  For example the 
                        key for the theta matrix which maps from the input layer to the first 
                        hidden layer is 1.
        """

        thetas = {1:np.reshape(params[0:self._architecture[1] * (self._architecture[0] + 1)], \
                              (int(self._architecture[1]), int((self._architecture[0] + 1))), order="F")}
         
        lastIndex = self._architecture[1] * (self._architecture[0] + 1) # index of the last weight for the first layer in the vector
        
        for layer in self._architecture.keys()[2:]:
            thetas[layer] = np.reshape(params[lastIndex:lastIndex + (self._architecture[layer] * (self._architecture[layer-1] + 1))], \
                                      (int(self._architecture[layer]), int((self._architecture[layer-1] + 1))), order="F")
            lastIndex = lastIndex + (self._architecture[layer] * (self._architecture[layer-1] + 1))
        
        return thetas
        
    def sigmoid(self, z):
        """
            Sigmoid Logistic Function - acts as activation of units/neruons.
            http://www.wolframalpha.com/input/?i=graph+sigmoid+function+from+-5+to+5
            
            parameters:
            
                z: <numpy-array> or <float> vector of inputs or single value which activates
                   the logistic units.
            
            returns:

                <numpy-array> or <float> vector of activations or single value activation for the
                the layer.
        """
        return (1/ (1 + np.exp(-z)))
    
    def sigmoidGradient(self, activation):
        """
            Calculates the derivative of the sigmoid activation function.  This derivative can
            be written as :
            
                sigmoid(z)*(1-sigmoid(z)) => acitvation*(1-activation)
                http://www.ai.mit.edu/courses/6.892/lecture8-html/sld015.htm
            
            parameters:
            
                activation: <numpy-array> or <float> vector of activations or single valued activation
                            produced by the sigmoid function.
            
            returns:
            
                <numpy-array> or <float> the derivative of the sigmoid function.
        """
        return np.multiply(activation, (1 - activation))

    def labelsToIndicatorFunction(self, targets):
        """
            The indicator function maps the targets for a classification problem from
            integers to vectors of 1's and 0's.  For a 3 class problem the targets are
            mapped as shown below:
            
                target      indicator function
                   1             [1, 0, 0]
                   2             [0, 1, 0]
                   3             [0, 0, 1]
            
            This implementation assumes that labels are indexed from 1 not 0.
            
            parameters:
            
               targets: <numpy-array> 1xm vector of discrete class labels/targets.
            
            returns:
            
                indicatorFunction: <numpy-array> kxm array, where k is the number of classes
                                   and m the number of training examples.  The indicator function 
                                   produces a kx1 vector denoting which class a given training example 
                                   belongs to.
        """
        # get the number of discrete classes
        numClasses = len(np.unique(targets))
        # intialise the indicator function to an array fo zeros
        indicatorFunction = np.zeros((np.shape(targets)[0], numClasses))
        # loop through each training example and produce the indicator function
        for i in range(np.shape(targets)[0]):
            indicatorFunction[i,int(targets[i])] = 1  # vector of 0's except for the index corresponding to the target
        return indicatorFunction.transpose() # transpose so correct for comparison with hypothesis
        
    def feedForward(self, thetas, input, regTerm, m):  

        # setup some variables for the calculation        
        activs = {1:input} # activation of the input layer is the input
        
        ### Forward Propagation ###
        # calculate the mapping of the input between all layers except the output layer.
        # While doing this calculate the regularisation term to avoid looping through layers
        # a second time.

        for layer in thetas.keys()[:-1]:
            z = np.dot(thetas[layer], activs[layer])
            activs[layer+1] = np.concatenate((np.tile(1, (1, m)), self.sigmoid(z)), axis=0) # add bias unit
            regTerm += np.sum(np.multiply(thetas[layer][:,1:], thetas[layer][:,1:]))
        regTerm += np.sum(np.multiply(thetas[thetas.keys()[-1]][:,1:], thetas[thetas.keys()[-1]][:,1:]))
        # calculate the activation of the output layer also known as the hypothesis
        z = np.dot(thetas[thetas.keys()[-1]], activs[activs.keys()[-1]])

        hypothesis = self.sigmoid(z)
        # checks for numerical instabilities
        if 1 in hypothesis:
            # np.log(1-1) = np.log(0) = -inf ( divide by zero encountered in log)
            # subtract off small number from 1
            hypothesis[np.where(hypothesis == 1)] = hypothesis[np.where(hypothesis == 1)] - 1e-9
        if 0 in hypothesis:
            # np.log(0) = -inf ( divide by zero encountered in log)
            hypothesis[np.where(hypothesis == 0)] = hypothesis[np.where(hypothesis == 0)] + 1e-9

        return hypothesis, activs, regTerm
        
    def backProp(self, thetas, hypothesis, activs, targets, m):
        """
            blah
        """
        deltas = {} # dictionary to store errors for each layer during back prop 
        grads = {} # dictionary to store gradients for each layer during back prop 
        
        ### Back Propagation ###
        numLayers = len(self._architecture.keys())
        deltas[numLayers] = np.subtract(hypothesis, targets)
        
        for layer in range(numLayers, 2, -1):
            deltas[layer-1] = np.multiply(np.dot(thetas[layer-1].transpose(), deltas[layer]), \
                                            self.sigmoidGradient(activs[layer-1]))
            deltas[layer-1] = deltas[layer-1][1:,:]
            
        for layer in thetas.keys():
            grad = 1/m * (np.dot(deltas[layer+1], activs[layer].transpose()))
            grad[:,1:] = grad[:,1:] + 1/m * (self._LAMBDA * thetas[layer][:,1:])
            grads[layer] = grad
    
        gradients = np.ravel(grads[1], order="F")
        for layer in grads.keys()[1:]:
            gradients = np.concatenate((gradients, np.ravel(grads[layer], order="F")), axis=0)  

        return gradients
    
    def costFunction(self, params, input, targets):
        """
            Computes the cost and gradient of the NerualNet model.  The implementation
            is vectorized back propagation as discussed in:
            
            https://www.coursera.org/course/ml - Coursera introduction to machine learning
            
            parameters:
            
                params: <numpy-array> a vector containing the current weights for all connections i
                        the NeuralNet.
            
                input: <numpy-array> an (n+1)xm array of m training examples each with n features and a bias unit.
            
                targets: <numpy-array> a kxm array of m trainging examples with k target values for each.
            
            returns:
            
                cost: <float> the cost of the NerualNet model given the current NeuralNet parameters (weights).
            
                gradients: <numpy-array> a vector containing the gradients for each connection of the NerualNet 
                           model.  The gradients are required by optimization algorithms e.g. scipy.fmincg in order
                           to minimise the cost during training.

        """
    
        
        # setup some variables for the calculation
        thetas = self.reshapeParams(params) # reshape the vecotr into matrices
        m = float(np.shape(input)[1]) # get the number of training examples
        regTerm = 0 # varaible to accumulate regularisation terms

        ### Feed the inputs forward though the network
        hypothesis, activations, regTerm = self.feedForward(thetas, input, regTerm, m)
        
        ### Cost Function Calculation ###
        # add the last theta term to the regularisation calulation
        cost = np.sum(np.multiply(-targets, np.log(hypothesis)) - \
                      np.multiply((1-targets), (np.log(1-hypothesis))))
        
        cost = 1/m * (cost + (self._LAMBDA*0.5*regTerm))
        
        ### Backpropagate errors though network ###
        gradients = self.backProp(thetas, hypothesis, activations, targets, m)

        return cost, gradients

    def computeNumericalGradient(self, func, params, *args):
            
        input, targets = args
        numgrad = np.zeros(np.shape(params))
        perturb = np.zeros(np.shape(params))
        epsilon = 0.0001
        for i in range(len(params)):
            perturb[i] = epsilon
            loss1 = func((params - perturb), input, targets)
            loss2 = func((params + perturb), input, targets)
            numgrad[i] = (loss2 - loss1) / (2.0 * epsilon)
            perturb[i] = 0
        return numgrad
    
    def checkGradients(self):
        
        def costFunction(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return cost
        
        def costFunctionGradient(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return grad
        
        input = np.copy(self._input[:10,:5])
        self._architecture = {0:9, 1:5, 2:3}
        params = self.initialise()
        thetas = self.reshapeParams(params)
        targets = self.labelsToIndicatorFunction(np.array([0, 1, 2, 0, 1])).transpose()
        args = (input, targets)
        grad = costFunctionGradient(params, *args)
        numgrad = self.computeNumericalGradient(costFunction, params, *args)
        print np.shape(numgrad), np.shape(grad)
        for i in range(len(numgrad)):
            print "%d\t%f\t%f" % (i, numgrad[i], grad[i])
        
        print "The above two columns you get should be very similar."
        print "(Left-Your Numerical Gradient, Right-Analytical Gradient)"
        
        print "If your backpropagation implementation is correct, then"
        print "the relative difference will be small (less than 1e-9). "
        
        diff = numgrad-grad
        print diff

    def train(self, retry=3):
        """
            train the network
        """
        from scipy import optimize
        
        def costFunction(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return cost
                
        def costFunctionGradient(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return grad
        
        print
        print "Training %s..." % self.search()
        print
            
        try:
            targets = self._indicatorFunction
        except AttributeError:
            targets = self._targets
            
        # attempting to handle the case where the the optimization raises the following warning:
        #        Warning: Desired accuracy not necessarily achieved due to percision loss.
        #
        # This seems to mean that the function was unable to calculate a gradient(?) could mean we
        # have randomly initialised the parmaters in a bad (flat) region of the parameter space. This
        # seems to be supported by the fact that it usually happpens after 1 iteration.  Trying to solve 
        # it by catching the warning and allowing the network to retry with a new randomly initialised set
        # of parameters a number of times.
        # Seems the warning is just a print statement not a real warning, so going to have to capture the 
        # the print statement and search for the string and control flow based on that.
        
        args = (self._input, targets)
        counter = 0
        output = [] # list to pass to Capturing to store print statements
        while counter <= retry:
            if counter > 0:
                print
                print "Training %s (Attempt: %d)..." % (self.search(), counter+1)
                print
            initialParams = self.initialise()
            with Capturing(output) as output:
                params = optimize.fmin_cg(costFunction, x0=initialParams, fprime=costFunctionGradient, \
                                              args=args, maxiter = self._maxiter)
            print output[counter]
            if "Warning" in output[counter]:
                if counter == retry:
                    print "Optimisation has failed %d times. Aborting training!" % (counter+1)
                print "Optimisation failed on attempt number %d!" % (counter+1)
                counter += 1
                continue
            self._trainedParams = params
            break

    def callback(self, params):
        #TODO
        global iteration, x_max
        sys.stdout.write("Iteration | %d\r" % (iteration))
        sys.stdout.flush()
        if interation % 10 == 0:
            cost, grad = self.costFunction(params, self._input, self._targets)
            costs.append(cost)
            iters.append(iteration)
            plt.plot(iters, costs)
        iteration += 1

    def predict_proba(self, input):
        
        thetas = self.reshapeParams(self._trainedParams)
        m = int(np.shape(input)[1]) # get the number of examples
        input = np.concatenate((np.tile(1, (1, m)), input), axis=0) # add bias units
        hypothesis, activations, regTerm = self.feedForward(thetas, input, regTerm=0, m=m)
        pred = np.ones((m,2))
        pred[:,0] = pred[:,0] * (1-hypothesis)
        pred[:,1] = pred[:,1] * hypothesis
        return pred

    def generateSetupDict(self):
        neuralNetSetupDict = {}
        for key in self._architecture.keys():
            neuralNetSetupDict["architecture"+str(key)] = self._architecture[key]
        neuralNetSetupDict["LAMBDA"] = self._LAMBDA
        neuralNetSetupDict["trainedParams"] = self._trainedParams
        return neuralNetSetupDict

    def saveNetwork(self, outputFile):
        
        import scipy.io as sio
        neuralNetSetupDict = self.generateSetupDict()
        sio.savemat(outputFile, neuralNetSetupDict)
        print "Trained %s saved in %s" % (self.search(), outputFile)

class NeuralNetPerform(NeuralNet):
    """
        object:     NeuralNetPerform
        superclass: NeuralNet
        
        A NeuralNet object with performace indicator methods.
    """
    def __init__(self, input, targets, architecture={}, LAMBDA=0.0, classify=False, maxiter=100, saveFile=None):
        """
            
        """
        NeuralNet.__init__(self, input, targets, architecture, LAMBDA, False, maxiter, saveFile)

    def calculatePerformanceIndicators(self, input, labels, hypothesis, threshold):
        hypothesis = np.squeeze(hypothesis)
        labels = np.squeeze(labels)
        
        numberPositives = len(np.where(labels == 1)[0])
        numberNegatives = len(np.where(labels == 0)[0])
        
        positivePredictionsIndices = np.where(hypothesis >= threshold)[0]
        negativePredictionsIndices = np.where(hypothesis < threshold)[0]
        
        truePositivesIndices = np.where(labels[positivePredictionsIndices] == 1)[0]
        trueNegativesIndices = np.where(labels[negativePredictionsIndices] == 0)[0]
        numberTruePositives = len(truePositivesIndices)
        numberTrueNegatives = len(trueNegativesIndices)

        falsePositives = np.where(labels[positivePredictionsIndices] != 1)[0]
        falseNegatives = np.where(labels[negativePredictionsIndices] != 0)[0]
        #print len(falseNegatives)

        FPR = len(falsePositives) / float(numberNegatives) # FPR = FP/N
        
        TPR = numberTruePositives / float(numberPositives) # Recall

        try:
            Precision = numberTruePositives / float(numberTruePositives + len(falsePositives))
        except:
            Precision = 1
    
        return FPR, TPR, Precision

    def calculateF1Score(self, Precision, Recall):
        return (2*(Precision*Recall) / float(Precision + Recall))

    def plotROCCurve(self, input, labels, acceptableFPR=0.01, stepSize=1e-3, tolerance=1e-3, plot=True):
        """
            Generate a plot of false positive rate against false negative rate
            as the threshld is varied.
        
            input - data set on which to calculate ROC curve
            stepSize - how much to vary the threshold on each iteration
            acceptableFPR - the acceptable false positive rate, default to 0.01(1%)
                            to directly compare with Brink et al. 2013.
            tolerance - used when calculating the false negative rate for the acceptable FPR.
            It is the deviation from the acceptable FPR for which we can get a corresponding
            FNR as the calculated FPR may not be exactly equal to the acceptable FPR chosen.
        
            FNR is the Missed Detection Rate used in Brink et al. 2013 ... I think.
        """
    
        #m = float(np.shape(input)[1])
    
        hypothesis = self.predict(input)
        falsePositiveRates = []
        falseNegativeRates = []
        for threshold in np.arange(0.0,1.0,stepSize):
        
            #print self.calculatePerformanceIndicators(input, labels, hypothesis, threshold)
            FPR, TPR, Precision = self.calculatePerformanceIndicators(input, labels, hypothesis, threshold)
        
            FNR = 1 - TPR
            falsePositiveRates.append(FPR)
            falseNegativeRates.append(FNR)
        
            if (FPR) >= acceptableFPR-tolerance and (FPR) <= acceptableFPR+tolerance:
                resultingFNR = FNR
                optThreshold = threshold
        
        if plot:
            import matplotlib.pyplot as plt
            plt.title("ROC Curve")
            plt.xlabel("false negative rate")
            plt.ylabel("false positive rate")
            plt.plot(falseNegativeRates, falsePositiveRates)
            plt.plot(falseNegativeRates, acceptableFPR*np.ones(np.shape(falsePositiveRates)), \
                     "b--", label="%.1lf%% FPR" % (acceptableFPR*100))
            try:
                plt.plot(resultingFNR*np.ones(np.shape(falseNegativeRates)), falsePositiveRates, \
                         "r--", label="%.1lf%% FNR" % (resultingFNR*100))
                plt.plot(resultingFNR, acceptableFPR, "ko", label="threshold: %.3lf" % optThreshold)
            except:
                print "\nNo threshold found resulting in specified FPR: %f for LAMBDA: %f" % (acceptableFPR, self._LAMBDA)
                print "Setting the optimum threshold and corresponding FNR to 0."
                resultingFNR = 0
                optThreshold = 0
                print
            plt.legend()
            plt.show()
        try:    
            return falsePositiveRates, falseNegativeRates, optThreshold, resultingFNR
        except:
            print "\nNo threshold found resulting in specified FPR: %f for LAMBDA: %f" % (acceptableFPR, self._LAMBDA)
            print "Setting the optimum threshold and corresponding FNR to 0."
            resultingFNR = 0
            optThreshold = 0
            return falsePositiveRates, falseNegativeRates, optThreshold, resultingFNR

class Autoencoder(NeuralNet):
    """
        object:     Autoencoder
        superclass: NeuralNet
    """
    def __init__(self, input, architecture={}, LAMBDA=0.0, maxiter=100, saveFile=None):
        assert len(architecture.keys()) < 2, \
        "Autoencoder can only have 1 hidden layer e.g. {1:25} \n(This may change in future versions.)"
        NeuralNet.__init__(self, input, input, architecture, LAMBDA, False, maxiter, saveFile)

    def search(self):
        return "Autoencoder"

    def checkGradients(self):
        
        def costFunction(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return cost
        
        def costFunctionGradient(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return grad
        
        input = np.copy(self._input[:5,:10])
        self._architecture = {0:4, 1:3, 2:4}
        params = self.initialise()
        targets = input[:4,:]
        args = (input, targets)
        grad = costFunctionGradient(params, *args)
        numgrad = self.computeNumericalGradient(costFunction, params, *args)
        #print np.shape(numgrad), np.shape(grad)
        for i in range(len(numgrad)):
            print "%d\t%f\t%f" % (i, numgrad[i], grad[i])
        
        print "The above two columns you get should be very similar."
        print "(Left-Your Numerical Gradient, Right-Analytical Gradient)"
        
        print "If your backpropagation implementation is correct, then"
        print "the relative difference will be small (less than 1e-9). "
        
        diff = numgrad-grad
        print diff

    def encode(self, params, input):
        
        """
            blah
        """
        # reshape the network parameters into theta matirces
        thetas = self.reshapeParams(params)
        # define some useful variables
        m = np.shape(input)[1]
        input = np.concatenate((np.tile(1, (1, m)), input), axis=0) # add bias units
        # encode the input features to those represented by the hidden layer
        # in other words feed this input forward through the net until a2 is calculated
        z2 = np.dot(thetas[1], input)
        encodedFeatures = self.sigmoid(z2) # encoded features are the activations of the hidden nodes given a set of params
        return encodedFeatures

    def getLearnedFeatures(self):
        
        thetas = self.reshapeParams(self._trainedParams)
        return np.divide(thetas[1][:,1:], np.sqrt(np.sum(np.multiply(thetas[1][:,1:], thetas[1][:,1:]), axis=1)[:,np.newaxis]))
 
    def visualiseLearnedFeatures(self):
        """
            Visualise the features learned by the autoencoder
        """
        import matplotlib.pyplot as plt
        
        extent = np.sqrt(self._architecture[0]) # size of input vector is stored in self._architecture
        # number of rows and columns to plot (number of hidden units also stored in self._architecture)
        plotDims = np.rint(np.sqrt(self._architecture[1]))
        plt.ion()
        fig = plt.figure()
        plt.set_cmap("gnuplot")
        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=-0.6, hspace=0.1)
        learnedFeatures = self.getLearnedFeatures()
        for i in range(self._architecture[1]):
            image = np.reshape(learnedFeatures[i,:], (extent, extent), order="F") * 1000
            ax = fig.add_subplot(plotDims, plotDims, i)
            plt.axis("off")
            ax.imshow(image, interpolation="nearest")
        plt.show()
        raw_input("Program paused. Press enter to continue.")

class SparseAutoencoder(Autoencoder):
    
    """
        object:     SparseAutoencoder
        superclass: Autoencoder
    """
    def __init__(self, input, architecture={}, LAMBDA=0.0, RHO=0.0, BETA=0.0, maxiter=100, saveFile=None):
        Autoencoder.__init__(self, input, architecture, LAMBDA, maxiter, saveFile)
        self._RHO = RHO
        self._BETA = BETA

    def search(self):
        return "SparseAutoencoder"

    def backProp(self, thetas, hypothesis, activs, targets, rhoHat, m):

        delta3 = np.multiply(-(targets - hypothesis), self.sigmoidGradient(hypothesis))
        # calculate sparsity delta
        if self._BETA != 0:
            sparseDelta = (np.divide(-self._RHO, rhoHat) + \
                           np.divide((1 - self._RHO), (1-rhoHat)))[:,np.newaxis]

        delta2 = np.multiply((np.dot(thetas[2][:,1:].transpose(), delta3) + \
                             (self._BETA * sparseDelta)), \
                              self.sigmoidGradient(activs[2][1:,:]))
        #delta2 = delta2[1:,:]
        
        theta2Grad = np.zeros(np.shape(thetas[2]))
        theta1Grad = np.zeros(np.shape(thetas[1]))
        
        #theta2Grad[:,1:] = theta2Grad[:,1:] + (1/m) * np.dot(delta3, activs[2][1:,:].transpose()) + self._LAMBDA * thetas[2][:,1:]
        #theta2Grad[:,0] = theta2Grad[:,0] = (1/m * (np.sum(delta3, axis=1)))
        theta2Grad = theta2Grad + ((1/m) * np.dot(delta3, activs[2].transpose()))
        theta2Grad[:,1:] = theta2Grad[:,1:] + (self._LAMBDA * thetas[2][:,1:])

        #theta1Grad[:,1:] = theta1Grad[:,1:] + (1/m) * np.dot(delta2, activs[1][1:,:].transpose()) + self._LAMBDA * thetas[1][:,1:]
        #theta1Grad[:,0] = theta1Grad[:,0] = (1/m * (np.sum(delta2, axis=1)))
        theta1Grad = theta1Grad + ((1/m) * np.dot(delta2, activs[1].transpose()))
        theta1Grad[:,1:] = theta1Grad[:,1:] + (self._LAMBDA * thetas[1][:,1:])

        gradients = np.concatenate((np.ravel(theta1Grad, order="F"), np.ravel(theta2Grad, order="F")))
        return gradients

    def costFunction(self, params, input, targets):
    
        thetas = self.reshapeParams(params)
        m = float(np.shape(input)[1]) # get the number of training examples
        regTerm = 0 # varaible to accumulate regularisation terms
        cost = 0
        ### Feed the inputs forward though the network
        hypothesis, activations, regTerm = self.feedForward(thetas, input, regTerm, m)
        
        ### calculate the cost
        cost = cost + np.sum((0.5/m) * np.multiply((targets - hypothesis), (targets - hypothesis)))

        ### calculate sparsity term
        sparseTerm = 0
        if self._BETA != 0:
            rhoHat = 1/m * np.sum(activations[2][1:,:], axis = 1)
            sparseTerm = np.sum(self._RHO * np.log(np.divide(self._RHO, rhoHat)) + \
                               (1 - self._RHO) * np.log(np.divide((1 - self._RHO), (1 - rhoHat))))

        # add regularisation and sparsity terms to the cost
        cost = cost + (0.5*self._LAMBDA*regTerm) + (self._BETA * sparseTerm)
        gradients = self.backProp(thetas, hypothesis, activations, targets, rhoHat, m)

        return cost, gradients

    def generateSetupDict(self):
        """
            blah
        """
        neuralNetSetupDict = {}
        for key in self._architecture.keys():
            neuralNetSetupDict["architecture"+str(key)] = self._architecture[key]
        neuralNetSetupDict["LAMBDA"] = self._LAMBDA
        neuralNetSetupDict["trainedParams"] = self._trainedParams
        neuralNetSetupDict["RHO"] = self._RHO
        neuralNetSetupDict["BETA"] = self._BETA
        return neuralNetSetupDict

    def saveNetwork(self, outputFile):
        
        import scipy.io as sio
        neuralNetSetupDict = self.generateSetupDict()
        sio.savemat(outputFile, neuralNetSetupDict)
        print "Trained %s saved in %s" % (self.search(), outputFile)
 
class LinearDecoder(SparseAutoencoder):

    """
        object:     LinearDecoder
        superclass: SparseAutoencoder
    """
    def __init__(self, input, architecture={}, LAMBDA=0.0, RHO=0.0, BETA=0.0, maxiter=100, saveFile=None):
        SparseAutoencoder.__init__(input, architecture, LAMBDA, RHO, BETA, maxiter, saveFile)

    def search(self):
        return "LinearDecoder"

    def feedForward(self, thetas, input, regTerm, m):  
        """
            feed forward for the linear decoder (http://ufldl.stanford.edu/wiki/index.php/Linear_Decoders).
            
            activation function for the output layer is the identity function.
        """
        # setup some variables for the calculation        
        activs = {1:input} # activation of the input layer is the input
        
        ### Forward Propagation ###
        # calculate the mapping of the input between all layers except the output layer.
        # While doing this calculate the regularisation term to avoid looping through layers
        # a second time.
        for layer in thetas.keys()[:-1]:
            z = np.dot(thetas[layer], activs[layer])
            activs[layer+1] = np.concatenate((np.tile(1, (1, m)), self.sigmoid(z)), axis=0) # add bias unit
            regTerm += np.sum(np.multiply(thetas[layer][:,1:], thetas[layer][:,1:]))
        regTerm += np.sum(np.multiply(thetas[thetas.keys()[-1]][:,1:], thetas[thetas.keys()[-1]][:,1:]))
    
        # calculate the activation of the output layer also known as the hypothesis
        z = np.dot(thetas[thetas.keys()[-1]], activs[activs.keys()[-1]])
        # For this case of the linear decoder, the activation function for the outout layer
        # is the identity fucntion i.e. f(z) = z.
        hypothesis = z
        # checks for numerical instabilities
        if 1 in hypothesis:
            # np.log(1-1) = np.log(0) = -inf ( divide by zero encountered in log)
            # subtract off small number from 1
            hypothesis[np.where(hypothesis == 1)] = hypothesis[np.where(hypothesis == 1)] - 1e-9
        if 0 in hypothesis:
            # np.log(0) = -inf ( divide by zero encountered in log)
            hypothesis[np.where(hypothesis == 0)] = hypothesis[np.where(hypothesis == 0)] + 1e-9
        
        return hypothesis, activs, regTerm

    def backProp(self, thetas, hypothesis, activs, targets, rhoHat, m):
        
        # For the case of a linear decoder activation fuction for the output layer is just 
        # the identity function. The derivative is therefore 1.  The calculation of delta3
        # simplifies to:
        delta3 = -(targets - hypothesis)
        
        # calculate sparsity delta
        if self._BETA != 0:
            sparseDelta = (np.divide(-self._RHO, rhoHat) + \
                           np.divide((1 - self._RHO), (1-rhoHat)))[:,np.newaxis]
        
        delta2 = np.multiply((np.dot(thetas[2][:,1:].transpose(), delta3) + \
                              (self._BETA * sparseDelta)), \
                             self.sigmoidGradient(activs[2][1:,:]))
        #delta2 = delta2[1:,:]
        
        theta2Grad = np.zeros(np.shape(thetas[2]))
        theta1Grad = np.zeros(np.shape(thetas[1]))
        
        #theta2Grad[:,1:] = theta2Grad[:,1:] + (1/m) * np.dot(delta3, activs[2][1:,:].transpose()) + self._LAMBDA * thetas[2][:,1:]
        #theta2Grad[:,0] = theta2Grad[:,0] = (1/m * (np.sum(delta3, axis=1)))
        theta2Grad = theta2Grad + ((1/m) * np.dot(delta3, activs[2].transpose()))
        theta2Grad[:,1:] = theta2Grad[:,1:] + (self._LAMBDA * thetas[2][:,1:])
        
        #theta1Grad[:,1:] = theta1Grad[:,1:] + (1/m) * np.dot(delta2, activs[1][1:,:].transpose()) + self._LAMBDA * thetas[1][:,1:]
        #theta1Grad[:,0] = theta1Grad[:,0] = (1/m * (np.sum(delta2, axis=1)))
        theta1Grad = theta1Grad + ((1/m) * np.dot(delta2, activs[1].transpose()))
        theta1Grad[:,1:] = theta1Grad[:,1:] + (self._LAMBDA * thetas[1][:,1:])
        
        gradients = np.concatenate((np.ravel(theta1Grad, order="F"), np.ravel(theta2Grad, order="F")))
        return gradients

class SoftMaxClassifier(NeuralNet):

    """
        object:     SoftMaxClassifier
        superclass: NeuralNet
    """
    def __init__(self, input, targets, LAMBDA=0.0, maxiter=100, saveFile=None):
        architecture = {}
        NeuralNet.__init__(self, input, targets, architecture, LAMBDA, True, maxiter, saveFile)
        self._indicatorFunction = self.labelsToIndicatorFunction(self._targets)
        self._architecture = {0:np.shape(self._input)[0]-1, 1:np.shape(self._indicatorFunction)[0]}

    def search(self):
        return "SoftMaxClassifier"

    def feedForward(self, theta, input):
        activ = np.exp(np.dot(theta, input))
        hypothesis = np.divide(activ, np.sum(activ, axis=0))
        return hypothesis

    def backProp(self, theta, hypothesis, input, indicatorFunction, m):
        
        thetaGrad = np.zeros(np.shape(theta))
        #print np.dot((hypothesis - indicatorFunction), input.transpose())
        thetaGrad = (1/m*(thetaGrad + np.dot((hypothesis - indicatorFunction), input.transpose()))) \
                    + self._LAMBDA*theta
        gradients = np.ravel(thetaGrad, order="F")
        return gradients

    def costFunction(self, params, input, indicatorFunction):
        """
            blah
        """
        # setup some useful variables
        cost = 0
        regTerm = 0
        m = np.shape(input)[1] # input should be (n+1)xm
        theta = self.reshapeParams(params)[1]
        # feed foward
        hypothesis = self.feedForward(theta, input)
        # calculate cost
        cost = cost + ((-1/m) * (cost + np.sum(np.multiply(indicatorFunction, np.log(hypothesis)))))
        # calculate regularisation term to cost
        regTerm = regTerm + (self._LAMBDA/2.0 * np.sum(np.multiply(theta, theta)))
        # add regularisation to cost
        cost = cost + regTerm
        # back propagate errors
        gradients = self.backProp(theta, hypothesis, input, indicatorFunction, m)
        return cost, gradients
  
    def checkGradients(self):
        """
            blah
        """
        def costFunction(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return cost
        
        def costFunctionGradient(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return grad
        
        input = np.copy(self._input[:6,:5])
        self._architecture = {0:5, 1:3}
        params = self.initialise()
        theta = self.reshapeParams(params)[1]
        targets = self.labelsToIndicatorFunction(np.array([0, 1, 2, 0, 1]))
        args = (input, targets)
        grad = costFunctionGradient(params, *args)
        numgrad = self.computeNumericalGradient(costFunction, params, *args)
        for i in range(len(numgrad)):
            print "%d\t%f\t%f" % (i, numgrad[i], grad[i])
        
        print "The above two columns you get should be very similar."
        print "(Left-Your Numerical Gradient, Right-Analytical Gradient)"
        
        print "If your backpropagation implementation is correct, then"
        print "the relative difference will be small (less than 1e-9). "
        
        diff = numgrad-grad
        print diff

    def train(self):
        """
            train the network
        """
        from scipy import optimize
        
        def costFunction(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return cost
        
        def costFunctionGradient(params, *args):
            input, targets = args
            cost, grad = self.costFunction(params, input, targets)
            return grad
        
        print
        print "Training %s..." % self.search()
        print

        args = (self._input, self._indicatorFunction)
        initialParams = self.initialise()
        
        params = optimize.fmin_cg(costFunction, x0=initialParams, fprime=costFunctionGradient, \
                                  args=args, maxiter = self._maxiter)
        
        self._trainedParams = params

class DeepNeuralNet(NeuralNet):

    """
        object:     DeepNeuralNet
        superclass: NeuralNet
    """
    def __init__(self):
        raise NotImplementedError

    def search(self):
        return "DeepNeuralNet"

