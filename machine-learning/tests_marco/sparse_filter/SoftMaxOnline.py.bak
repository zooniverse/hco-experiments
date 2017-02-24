import sys
import numpy as np
import matplotlib.pyplot as plt

np.seterr(all="raise")

class SoftMaxOnline(object):

    def __init__(self, LAMBDA=0.0, alpha=0.1, verbose=False, isteps=10):

        self.LAMBDA = LAMBDA
        self.alpha = alpha
        self.verbose = verbose
        if self.verbose:
            import matplotlib.pyplot as plt
        self.isteps = isteps
        self.trainedParams = None
        
        self.costs = []
        self.iters = []
        self.initial_cost = None
    
    def search(self):
        return "SoftMaxOnline"
    
    def randInitialiseWeights(self, nIn, nOut):
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
        initialParams = np.ravel(self.randInitialiseWeights(self.architecture[0], \
                                                            self.architecture[1]), order="F")
        # loop through the remaining layers and intialise the weights
        for layer in self.architecture.keys()[1:-1]:
            initialParams = np.concatenate((initialParams, \
                            np.ravel(self.randInitialiseWeights(self.architecture[layer], \
                            self.architecture[layer+1]), \
                            order="F")), \
                            axis=0)
        return initialParams

    def reshapeParams(self, params):
        thetas = {1:np.reshape(params[0:self.architecture[1] * (self.architecture[0] + 1)], \
                               (self.architecture[1], (self.architecture[0] + 1)), order="F")}
            
        lastIndex = self.architecture[1] * (self.architecture[0] + 1) # index of the last weight for the first layer in the vector
                               
        for layer in self.architecture.keys()[2:]:
            thetas[layer] = np.reshape(params[lastIndex:lastIndex + (self.architecture[layer] * (self.architecture[layer-1] + 1))], \
            (self.architecture[layer], (self.architecture[layer-1] + 1)), order="F")
            lastIndex = lastIndex + (self.architecture[layer] * (self.architecture[layer-1] + 1))
                                                              
        return thetas

    def labelsToIndicatorFunction(self, y):
        # get the number of discrete classes
        numClasses = len(np.unique(y))
        # intialise the indicator function to an array fo zeros
        indicatorFunction = np.zeros((np.shape(y)[0], numClasses))
        # loop through each training example and produce the indicator function
        for i in range(np.shape(y)[0]):
            indicatorFunction[i,int(y[i])] = 1  # vector of 0's except for the index corresponding to the target
        return indicatorFunction.transpose() # transpose so correct for comparison with hypothesis

    def feedForward(self, theta, X):
        activ = np.exp(np.dot(theta, X))
        hypothesis = np.divide(activ+1e-9, np.sum(activ, axis=0))
        
        return hypothesis
    
    def backProp(self, theta, hypothesis, X, indicatorFunction, m):
        
        thetaGrad = np.zeros(np.shape(theta))
        #print np.shape(hypothesis), np.shape(indicatorFunction), np.shape(X.T)
        #print np.dot((hypothesis - indicatorFunction), X.transpose())
        thetaGrad = (1/m*(thetaGrad + np.dot((hypothesis - indicatorFunction), X.transpose()))) \
            + self.LAMBDA*theta
        gradients = np.ravel(thetaGrad, order="F")
        return gradients
    
    def costFunction(self, params, X, indicatorFunction):
        # setup some useful variables
        cost = 0
        regTerm = 0
        m = float(np.shape(X)[1]) # input should be (n+1)xm # Cast as float 6/11/14 to pass gradient check
        theta = self.reshapeParams(params)[1]
        # feed forward
        hypothesis = self.feedForward(theta, X)
        # calculate cost
        cost += ((-1/m) * (cost + np.sum(np.multiply(indicatorFunction, np.log(hypothesis)))))
        # calculate regularisation term to cost
        regTerm += (self.LAMBDA/2.0 * np.sum(np.multiply(theta, theta)))
        # add regularisation to cost
        cost += regTerm
        # back propagate errors
        gradients = self.backProp(theta, hypothesis, X, indicatorFunction, m)
        return cost, gradients

    def stochastic_gradient_descent(self, f, x0, fprime, args):
        X, y = args
        m = np.shape(X)[1]
        stochastic_indices = np.random.permutation(m)
        for i,index in enumerate(stochastic_indices):
            sys.stdout.write("Iteration | %d\r" % (i))
            sys.stdout.flush()
            if i % self.isteps == 0 and self.verbose:
                if i == 0:
                    cost, grad = self.costFunction(x0, X, y)
                    self.initial_cost = cost
                #if i == 200:
                #    self.alpha = 0.01
                #else:
                #    self.alpha = 0.0001
                plt.clf()
                plt.ion()
                #try:
                #    cost, grad = self.costFunction(x0, input[:,:index], targets[:index])
                #except, ValueError:
                cost, grad = self.costFunction(x0, X, y)
                self.costs.append(cost)
                self.iters.append(i)
                plt.plot([0,len(stochastic_indices)], [self.initial_cost,self.initial_cost], "k--")
                plt.plot(self.iters, self.costs)
                plt.draw()
                
            # only pass a single training example for each iteration
            costGrad = fprime(x0, X[:,index][:,np.newaxis], y[:,index][:,np.newaxis])
            #print np.shape(x0), np.shape(costGrad)
            x0 = x0 - self.alpha*costGrad
        return x0

    def rmsProp(self, f, x0, fprime, args):
        X, y = args
        m = np.shape(X)[1]
        stochastic_indices = np.random.permutation(m)
        mean_square = 1
        for i,index in enumerate(stochastic_indices):
            sys.stdout.write("Iteration | %d\r" % (i))
            sys.stdout.flush()
            if i % self.isteps == 0 and self.verbose:
                if i == 0:
                    cost, grad = self.costFunction(x0, X, y)
                    self.initial_cost = cost
                cost, grad = self.costFunction(x0, X, y)
                self.costs.append(cost)
                self.iters.append(i)
                plt.plot([0,len(stochastic_indices)], [self.initial_cost,self.initial_cost], "k--")
                plt.plot(self.iters, self.costs)
                plt.draw()

            # only pass a single training example for each iteration                                                   

            costGrad = fprime(x0, X[:,index][:,np.newaxis], y[:,index][:,np.newaxis])

            mean_square = 0.9*mean_square - 0.1*(costGrad*costGrad)
            print mean_square
            x0 = x0 - self.alpha*(costGrad/np.sqrt(mean_square+1e-8))
        return x0
            
    def fit(self, X, y):
        """
            X is (m, n)
            y is (m,)
        """
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
        
        self.costs = []
        self.iters = []

        X = X.T # legacy of my original ANN code. Transpose X
                # so it matches sklearn API.
        n, m = np.shape(X) # get number of features before adding the bias unitOB
        X = np.concatenate((np.ones((1,m)), X), axis=0) # add bias unit to X
        indicatorFunction = self.labelsToIndicatorFunction(y)
        self.architecture = {0:n, 1:np.shape(indicatorFunction)[0]}
        args = X, indicatorFunction
        
        try:
            # self._trainedParams initialised as None, if this classifier has
            # has been trained already, then it will point to a matrix which
            # we want to use for online learning.
            assert self.trainedParams is not None
            initialParams = self.trainedParams
        except AssertionError:
            # if the classifier hasn't already been trained then we need to randomly
            # initialise the weights.
            initialParams = self.initialise()

        params = self.stochastic_gradient_descent(costFunction, x0=initialParams, \
                                                  fprime=costFunctionGradient, \
                                                  args=args)
        #params = self.rmsProp(costFunction, x0=initialParams, \
        #                      fprime=costFunctionGradient, \
        #                      args=args)

        self.trainedParams = params

    def predict(self, X):
        X = X.T # legacy of my original ANN code. Transpose X
                # so it matches sklearn API.
        n, m = np.shape(X)
        X = np.concatenate((np.ones((1,m)), X), axis=0)
        theta = self.reshapeParams(self._trainedParams)[1]
        hypothesis = self.feedForward(theta, X)
        return hypothesis
    
    def predict_proba(self, X):
        X = X.T # legacy of my original ANN code. Transpose X
                # so it matches sklearn API.
        n, m = np.shape(X)
        X = np.concatenate((np.ones((1,m)), X), axis=0)
        theta = self.reshapeParams(self.trainedParams)[1]
        hypothesis = self.feedForward(theta, X)
        return hypothesis.T
