import sys
import numpy as np
import scipy.io as sio

class SparseFilter(object):
    def __init__(self, k=256, channels=1, maxiter=200, saveFile=None):
        if saveFile == None:
            self.k = int(k)
            self.channels = int(channels)
            self.maxiter = int(maxiter)
            self.n = None
            self.trainedW = None
        else:
            import scipy.io as sio
            setup = sio.loadmat(saveFile)
            self.k = int(setup["k"])
            self.channels = int(setup["channels"])
            self.maxiter = int(setup["maxiter"])
            self.n = int(setup["n"])
            self.trainedW = setup["trainedW"]
        self.iteration = 0

    def fit(self, X):
        from scipy import optimize
        
        def objective(W, *args):
            X, pad = args
            Obj, DeltaW = self.objective(X, W)
            return Obj
        
        def objectiveG(W, *args):
            X, pad = args
            #print type(X)
            Obj, DeltaW = self.objective(X, W)
            return DeltaW
        
        n, m = np.shape(X)
        self.n = n
        args = (X, 1)
        initW = np.ravel(np.random.rand(self.k, n), order="F")
        optW = optimize.fmin_cg(objective, x0=initW, fprime=objectiveG, \
                                args=args, maxiter=self.maxiter, \
                                callback=self.callback)
        self.trainedW = optW

    def objective(self, X, W):
        #print np.shape(X)
        n, m = np.shape(X)
        W = np.reshape(W, (self.k, n), order="F")
        # Feed forward
        #print np.shape(W)
        #print np.shape(X)
        F = np.dot(W, X)
        #print np.shape(F)
        Fs = np.sqrt(np.multiply(F, F) + 1e-8)
        NFs, L2Fs = self.l2row(Fs)
        Fhat, L2Fn = self.l2row(NFs.T)
        # Copute objective function
        #print np.shape(Fhat)
        Obj = self.objectiveFunc(Fhat)
        # backpropagate through each feed forward step
        DeltaW = self.l2rowg(NFs.T, Fhat, L2Fn, np.ones(np.shape(Fhat)))
        DeltaW = self.l2rowg(Fs, NFs, L2Fs, DeltaW.T)
        DeltaW = np.dot(np.multiply(DeltaW, (F/Fs)), X.T)
        #print np.shape(DeltaW)
        DeltaW = np.ravel(DeltaW, order="F")
        return Obj, DeltaW

    def l2row(self, X):
        n, m = np.shape(X)
        N = np.sqrt(np.sum(np.multiply(X, X), axis=1) + 1e-8)
        N_stack = np.tile(N, (m, 1)).T
        Y = np.divide(X, N_stack)
        return Y, N

    def objectiveFunc(self, Fhat):
        return np.sum(Fhat)

    def l2rowg(self, X, Y, N, D):
        n, m = np.shape(X)
        N_stack = np.tile(N, (m, 1)).T
        firstTerm = np.divide(D, N_stack)
        sum = np.sum(np.multiply(D, X), 1)
        sum = sum / (np.multiply(N,N))
        sum_stack = np.tile(sum[np.newaxis], (np.shape(Y)[1],1)).T
        secondTerm = np.multiply(Y, sum_stack)
        return firstTerm - secondTerm

    def feedForward(self, W, X):
        # Feed Forward
        n, m = np.shape(X)
        W = np.reshape(W, (self.k, self.n), order="F")
        F = np.dot(W, X)
        Fs = np.sqrt(np.multiply(F, F) + 1e-8)
        NFs, L2Fs = self.l2row(Fs)
        Fhat, L2Fn = self.l2row(NFs.T)


    def callback(self, W):
        sys.stdout.write("Iteration | %d\r" % (self.iteration))
        sys.stdout.flush()
        self.iteration += 1

    def visualiseLearnedFeatures(self):
        import matplotlib.pyplot as plt
        W = np.reshape(self.trainedW, (self.k, self.n), order="F")
        # each row of W is a learned feature
        extent = np.sqrt(self.n/self.channels)
        #image = np.zeros((extent,extent,self.channels),dtype="float")
        #print np.shape(image)
        fig = plt.figure(facecolor="w")
        plt.ion()
        plotDims = int(np.ceil(np.sqrt(self.k)))
        for i in range(1,self.k+1):
            image = np.zeros((extent,extent,self.channels),dtype="float")
            ax = fig.add_subplot(plotDims, plotDims, i)
            for j in range(1,self.channels+1):
                #print (j-1)*extent*extent, j*extent*extent
                image[:,:,j-1] += \
                np.reshape(W[i-1,(j-1)*extent*extent:j*extent*extent], \
                (extent, extent), order="F")
                #image[:,:,j-1] = img_scale.sqrt(image[:,:,j-1], scale_min=0, \
                                    #scale_max=10)
                image[:,:,j-1] = image[:,:,j-1]/np.max(image[:,:,j-1])
            #image = np.reshape(W[i-1,:], (extent, extent))
            #max = np.max(np.abs(image))
            #print np.shape(image)
            #ax.imshow(image[:,:,0], cmap="gray")
            #image = (255*image).astype(np.uint8)
            image = image + 1
            image = image / 2.0
            cmap = "jet"
            if self.channels == 1:
                image = image[:,:,0]
                cmap = "binary"
            ax.imshow(image, interpolation="nearest", cmap=cmap)
            plt.axis("off")
        plt.ioff()
        plt.show()

    def saveSF(self, outFile):
        import scipy.io as sio
        output = open(outFile, "w")
        sio.savemat(output, {"k":int(self.k), "channels":int(self.channels), 
                             "n":int(self.n), "maxiter":int(self.maxiter),
                             "trainedW": self.trainedW})

def computeNumericalGradient(func, params, *args):
    """
        Calculate the numerical apporximation to function gradients
    """
    
    data = args[0]
    numgrad = np.zeros(np.shape(params))
    perturb = np.zeros(np.shape(params))
    e = 0.0001
    for i in range(len(params)):
        # set perturbation vector
        perturb[i] = e
        loss1 = func((params - perturb), data)
        loss2 = func((params + perturb), data)
        # Compute Numerical Gradient
        numgrad[i] = (loss2 - loss1) / (2.0*e)
        perturb[i] = 0
    return numgrad

def checkGradients():

    def costFunction(W, *args):
        def l2row(X):
            n, m = np.shape(X)
            N = np.sqrt(np.sum(np.multiply(X, X), axis=1) + 1e-8)
            N_stack = np.tile(N, (m, 1)).T
            Y = np.divide(X, N_stack)
            return Y, N
        
        def l2rowg(X, Y, N, D):
            n, m = np.shape(X)
            N_stack = np.tile(N, (m, 1)).T
            firstTerm = np.divide(D, N_stack)
            sum = np.sum(np.multiply(D, X), 1)
            sum = sum / (np.multiply(N,N))
            sum_stack = np.tile(sum[np.newaxis], (np.shape(Y)[1],1)).T
            secondTerm = np.multiply(Y, sum_stack)
            return firstTerm - secondTerm
        
        X = args[0]
        n, m = np.shape(X)
        W = np.reshape(W, (k, n), order="F")
        # Feed forward
        F = np.dot(W, X)
        Fs = np.sqrt(np.multiply(F, F) + 1e-8)
        NFs, L2Fs = l2row(Fs)
        Fhat, L2Fn = l2row(NFs.T)
        # Compute objective function
        return np.sum(Fhat)

    k = 40
    n = 20
    # initialise
    #W = np.array([[1,2],[3,4],[5,6],[7,8]])/10.0
    W = np.random.rand(int(k),int(n))
    #print np.shape(W)
    W = np.ravel(W, order="F")
    dataFile = "../data/naturalImages_patches_8x8.mat"
    data = sio.loadmat(dataFile)
    X = data["patches"][:n,:20]
    args = X, k
    
    sf = SparseFilter(k,1)
    cost, grad = sf.objective(X, W)
    numgrad = computeNumericalGradient(costFunction, W, *args)
    for i in range(len(numgrad)):
        print "%d\t%f\t%f" % (i, numgrad[i], grad[i])
        
    print "The above two columns you get should be very similar."
    print "(Left-Your Numerical Gradient, Right-Analytical Gradient)"
    print
    print "If your backpropagation implementation is correct, then"
    print "the relative difference will be small (less than 1e-9). "
    
    diff = numgrad-grad
    #print "Relative Difference: %f" % diff
    print diff

def main():
    #checkGradients()

    dataFile = "/Users/dew/development/PS1-Real-Bogus/data/3pi/"+\
               "3pi_20x20_signPreserveNorm.mat"

    #dataFile = "/Users/dew/development/PS1-Real-Bogus/data/3pi/"+\
    #                   "patches_3pi_20x20_signPreserveNorm_8x8_10.mat"

    data = sio.loadmat(dataFile)

    #X = data["patches"][:40000,:].T
    X = data["X"].T
    sf = SparseFilter()
    sf.fit(X)
    sf.saveSF("SF_256_"+dataFile.split("/")[-1].split(".")[0]+".mat")
    sf.visualiseLearnedFeatures()

if __name__ == "__main__":
    main()
