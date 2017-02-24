import optparse, sys, multiprocessing

import numpy as np
import scipy.io as sio
import scipy.signal as sig

from sparseFilter import SparseFilter
from NeuralNetMulti import SoftMaxClassifier

from sklearn.metrics import roc_curve
from sklearn import preprocessing

try:
    import cPickle as pickle
except ImportError:
    import pickle

sys.path.insert(1,"../tools/")
import multiprocessingUtils

def one_percent_mdr(y, pred):
    fpr, tpr, thresholds = roc_curve(y, pred)
    FoM = fpr[np.where(1-tpr<=0.01)[0][0]] # FPR at 1% MDR
    threshold = thresholds[np.where(1-tpr<=0.01)[0][0]]
    return FoM, threshold

def one_percent_fpr(y, pred):
    fpr, tpr, thresholds = roc_curve(y, pred)
    FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]] # MDR at 1% FPR
    threshold = thresholds[np.where(fpr<=0.01)[0][-1]]
    return FoM, threshold

class train_SoftMax_task(multiprocessingUtils.Task):
    #def __init__(self, C, fold, X, Y, testX, testY, s1, s2, s3, s4, fom_func=one_percent_mdr):
    #def __init__(self, C, fold, X, Y, testX, testY, fom_func=one_percent_mdr):
    def __init__(self, C, fold, fom_func=one_percent_mdr):
        self.C = C
        self.fold = fold
        """
        self.X = self.to_numpy_array(X,s1)
        self.Y = self.to_numpy_array(Y,s2)
        self.testX = self.to_numpy_array(testX,s3)
        self.testY = self.to_numpy_array(testY,s4)
        """
        """
        self.X = X
        self.Y = Y
        self.testX = testX
        self.testY = testY
        """
        self.fom_func = fom_func

    def __call__(self):
        #clf = SoftMaxClassifier(self.X, self.Y, LAMBDA=self.C, maxiter=10000)
        clf = SoftMaxClassifier(folds[self.fold]["X"], folds[self.fold]["Y"], LAMBDA=self.C, maxiter=10000)
        clf.train()
        #pred = clf.predict(self.testX).T
        pred = clf.predict(folds[self.fold]["testX"]).T
        indices = np.argmax(pred, axis=1)
        pred = np.max(pred, axis=1)
        pred[indices==0] = 1 - pred[indices==0]
    
        #FoM, threshold = self.fom_func(self.testY, pred)
        FoM, threshold = self.fom_func(folds[self.fold]["testY"], pred)
        return FoM, threshold, self.C, self.fold

    def __str__(self):
        return "Training Softmax Classifier with LAMBDA=%e" % (self.C)
    """
    def to_numpy_array(self, S, s):
        S_numpy = ctypeslib.as_array(S)
        S_numpy.shape = s
        return S_numpy
    """
class convolve_and_pool_task(multiprocessingUtils.Task):

    def __init__(self, convPart, patchDim, poolDim, stepSize, trainImages, testImages, W):
        self.convPart = convPart
        self.patchDim = patchDim
        self.poolDim = poolDim
        self.stepSize = stepSize
        self.trainImages = trainImages
        self.testImages = testImages
        self.W = W
        
        self.featureStart = self.convPart*self.stepSize
        self.featureEnd = (self.convPart+1)*self.stepSize
    
    def __call__(self):
        Wt = self.W[self.featureStart:self.featureEnd, :]
        convolvedFeaturesThis = convolve(self.patchDim, self.stepSize, self.trainImages, Wt)
        pooledFeaturesThisTrain = pool(self.poolDim, convolvedFeaturesThis)
        if np.any(self.testImages):
            print 'Convolving and pooling test images\n'
            convolvedFeaturesThis = convolve(self.patchDim, self.stepSize, self.testImages, Wt)
            pooledFeaturesThisTest = pool(self.poolDim, convolvedFeaturesThis)
        return pooledFeaturesThisTrain, pooledFeaturesThisTest, self.featureStart, self.featureEnd
        
    def __str__(self):
        return 'Step %d: features %d to %d\n'% (self.convPart, self.featureStart, self.featureEnd)
"""
class convolve_and_pool_task(multiprocessingUtils.Task):
    def __init__(self, convPart, patchDim, poolDim, stepSize, trainImages, testImages, W):
        self.convPart = convPart
        self.patchDim = patchDim
        self.poolDim = poolDim
        self.stepSize = stepSize
        self.trainImages = trainImages
        self.testImages = testImages
        self.W = W
        
        self.featureStart = self.convPart*self.stepSize
        self.featureEnd = (self.convPart+1)*self.stepSize
    
    def __call__(self):
        Wt = self.W[self.featureStart:self.featureEnd, :]
        convolvedFeaturesThis = convolve(self.patchDim, self.stepSize, self.trainImages, Wt)
        pooledFeaturesThisTrain = pool(self.poolDim, convolvedFeaturesThis)
        if np.any(self.testImages):
            print 'Convolving and pooling test images\n'
            convolvedFeaturesThis = convolve(self.patchDim, self.stepSize, self.testImages, Wt)
            pooledFeaturesThisTest = pool(self.poolDim, convolvedFeaturesThis)
        return pooledFeaturesThisTrain, pooledFeaturesThisTest, self.featureStart, self.featureEnd
        
    def __str__(self):
        return 'Step %d: features %d to %d\n'% (self.convPart, self.featureStart, self.featureEnd)
"""

class convolve_and_pool_task(multiprocessingUtils.Task):
    def __init__(self, patchDim, poolDim, stepSize, images, Wt, featureStart, featureEnd, i):
        self.patchDim = patchDim
        self.poolDim = poolDim
        self.stepSize = stepSize
        self.images = images
        self.Wt = Wt
    
        self.featureStart = featureStart
        self.featureEnd = featureEnd
        self.i = i
    
    def __call__(self):
        convolvedFeaturesThis = convolve(self.patchDim, self.stepSize, self.images, self.Wt)
        pooledFeaturesThis = pool(self.poolDim, convolvedFeaturesThis)
        return pooledFeaturesThis, self.featureStart, self.featureEnd, self.i, self.images.shape[3]
        
    def __str__(self):
        return 'convolving stamp %d: features %d to %d\n'% (self.i, self.featureStart, self.featureEnd)

def convolve(patchDim, numFeatures, images, W):
    m = np.shape(images)[3]
    imageDim = np.shape(images)[0]
    imageChannels = np.shape(images)[2]
    convolvedFeatures = np.zeros((numFeatures, m, \
                        imageDim - patchDim + 1, imageDim - patchDim + 1))
    for imageNum in range(m):
        for featureNum in range(numFeatures):
            convolvedImage = np.zeros((imageDim - patchDim + 1, imageDim - patchDim + 1))
            for channel in range(imageChannels):
                feature = np.zeros((patchDim, patchDim))
                start = channel * patchDim*patchDim
                stop = start + patchDim*patchDim
                feature += np.reshape(W[featureNum, start:stop], (patchDim, patchDim), order="F")
                feature = np.flipud(np.fliplr(feature))
                im = images[:, :, channel, imageNum]
                convolvedImage += sig.convolve2d(im, feature, "valid")
            # sparse filtering activation function
            convolvedImage = np.sqrt(1e-8 + np.multiply(convolvedImage, convolvedImage))
            convolvedFeatures[featureNum, imageNum, :, :] = convolvedImage
    return convolvedFeatures

def pool(poolDim, convolvedFeatures):
    numImages = np.shape(convolvedFeatures)[1]
    numFeatures = np.shape(convolvedFeatures)[0]
    convolvedDim = np.shape(convolvedFeatures)[2]

    pooledFeatures = np.zeros((numFeatures, numImages, int(np.floor(convolvedDim/float(poolDim))), \
                               int(np.floor(convolvedDim/float(poolDim)))))

    for imageNum in range(numImages):
        for featureNum in range(numFeatures):
            for i in range(int(np.floor(convolvedDim/float(poolDim)))):
                for j in range(int(np.floor(convolvedDim/float(poolDim)))):
                   starti = i*poolDim                   
                   startj = j*poolDim
                   stopi = (i+1)*poolDim
                   stopj = (j+1)*poolDim
                   ### pooling changed from np.mean to np.sum 13/01/15 ###
                   pooledFeatures[featureNum,imageNum,i,j] += \
                   np.sum(convolvedFeatures[featureNum,imageNum,starti:stopi,startj:stopj])
    return pooledFeatures

def get_sparseFilter(numFeatures, patches, patchesFile, maxiter=100):
    try:
        # added maxiter to filename 24/02/15
        sf_file = "trained_sparseFilters/SF_%d_%s_maxiter%d.mat" % \
        (numFeatures, patchesFile.split("/")[-1].split(".")[0], maxiter)
        print sf_file
        SF = SparseFilter(saveFile=sf_file)
        print "[*] Trained sparse filter loaded."
    except IOError:
        print "[*] Could not find trained sparse filter."
        print "[+] Training sparse filter ... "
        SF = SparseFilter(k=numFeatures, maxiter=maxiter)
        SF.fit(patches)
        SF.saveSF(sf_file)
        print "[+] Sparse filter trained"
    #SF.visualiseLearnedFeatures()
    return SF

def load_data(dataFile, imageDim):
    """
        currently only works for single channel images
        2 feb 2015:
            added imageDim argument to fix hard coding 
            image dimensions.
    """ 
    try:
        data = sio.loadmat(dataFile)
    except IOError:
        print "[!] Exiting: could not open patches file - %s" % patchesFile
        exit(0)
    
    data = sio.loadmat(dataFile)
    try:
        X = np.concatenate((data["X"], data["validX"]))
        y = np.concatenate((data["y"], data["validy"]))
    except KeyError:
        X = data["X"]
        try:
            y = data["y"]
        except KeyError:
            y = np.ones((np.shape(X)[0],))
    try:
        testX = data["testX"]
        testy = data["testy"]
    except KeyError:
        testImages = testLabels = testy = numTestImages = None
    ### Added scaling 06/01/15 ###
    #scaler = preprocessing.StandardScaler(with_std=False).fit(X)
    #X = scaler.transform(X)
    numTrainImages, n = np.shape(X)
    print numTrainImages
    try:
        trainLabels = y
    except NameError:
        trainLabels = np.ones((numTrainImages,))
    trainImages = np.zeros((imageDim,imageDim,1,numTrainImages))
    for i in range(numTrainImages):
        image = np.reshape(X[i,:], (imageDim,imageDim), order="F")
        trainImages[:,:,0,i] = trainImages[:,:,0,i] + image
    X = None

    if np.any(testy):
        ### Added scaling 06/01/15 ###
        #testX = scaler.transform(testX)
        numTestImages, n = np.shape(testX)
        testLabels = data["testy"]
        testImages = np.zeros((imageDim,imageDim,1,numTestImages))
        for i in range(numTestImages):
            image = np.reshape(testX[i,:], (imageDim,imageDim), order="F")
            testImages[:,:,0,i] = testImages[:,:,0,i] + image
        testX = None
    data = None


    return trainImages, trainLabels, numTrainImages,\
           testImages, testLabels, numTestImages

"""
def convolve_and_pool(dataFile, featuresFile, W, imageDim, patchDim, poolDim, numFeatures, stepSize):

    trainImages, trainLabels, numTrainImages,\
    testImages, testLabels, numTestImages = load_data(dataFile, imageDim)
    print testImages
    pooledFeaturesTrain = np.zeros((numFeatures,numTrainImages, \
                                    int(np.floor((imageDim-patchDim+1)/poolDim)), \
                                    int(np.floor((imageDim-patchDim+1)/poolDim))))
    if np.any(testImages):
        pooledFeaturesTest = np.zeros((numFeatures,numTestImages, \
                                       int(np.floor((imageDim-patchDim+1)/poolDim)), \
                                       int(np.floor((imageDim-patchDim+1)/poolDim))))

    taskList = []
    cpu_count = multiprocessing.cpu_count()

    for convPart in range(numFeatures/stepSize):
        taskList.append(convolve_and_pool_task(convPart, patchDim, poolDim, \
                                               stepSize, trainImages, testImages, W))

    resultsList = multiprocessingUtils.multiprocessTaskList(taskList, cpu_count)

    for result in resultsList:
        pooledFeaturesTrain[result[2]:result[3], :, :, :] += result[0]
        pooledFeaturesTest[result[2]:result[3], :, :, :] += result[1]

    print pooledFeaturesTrain

    if np.any(testImages):
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain, \
                     "pooledFeaturesTest":pooledFeaturesTest})
    else:
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain})
"""

def convolve_and_pool(dataFile, featuresFile, W, imageDim, patchDim, poolDim, numFeatures, stepSize):

    batchSize = 1

    trainImages, trainLabels, numTrainImages,\
    testImages, testLabels, numTestImages = load_data(dataFile, imageDim)
    pooledFeaturesTrain = np.zeros((numFeatures,numTrainImages, \
                                    int(np.floor((imageDim-patchDim+1)/poolDim)), \
                                    int(np.floor((imageDim-patchDim+1)/poolDim))))
    
    taskList = []
    cpu_count = multiprocessing.cpu_count()
    
    for convPart in range(numFeatures/stepSize):
        for i in range(0,numTrainImages,batchSize):
            featureStart = convPart*stepSize
            featureEnd = (convPart+1)*stepSize
            Wt = W[featureStart:featureEnd, :]
            taskList.append(convolve_and_pool_task(patchDim, poolDim, stepSize, \
                                                   trainImages[:,:,:,i:(i+1)*batchSize], Wt, \
                                                   featureStart, featureEnd, i))

    resultsList = multiprocessingUtils.multiprocessTaskList(taskList, cpu_count)

    for result in resultsList:
        pooledFeaturesTrain[result[1]:result[2], result[3]:result[3]+result[4], :, :] += result[0]
    
    
    if np.any(testImages):
        pooledFeaturesTest = np.zeros((numFeatures,numTestImages, \
                                       int(np.floor((imageDim-patchDim+1)/poolDim)), \
                                       int(np.floor((imageDim-patchDim+1)/poolDim))))
        taskList = []
        
        for convPart in range(numFeatures/stepSize):
            for i in range(0,numTrainImages,batchSize):
                featureStart = convPart*stepSize
                featureEnd = (convPart+1)*stepSize
                Wt = W[featureStart:featureEnd, :]
                taskList.append(convolve_and_pool_task(patchDim, poolDim, stepSize, \
                                                       testImages[:,:,:,i:(i+1)*batchSize], Wt, \
                                                       featureStart, featureEnd, i))

        resultsList = multiprocessingUtils.multiprocessTaskList(taskList, cpu_count)

    for result in resultsList:
        pooledFeaturesTest[result[1]:result[2], result[3]:result[3]+result[4], :, :] += result[0]

    if np.any(testImages):
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain, \
                     "pooledFeaturesTest":pooledFeaturesTest})
    else:
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain})

def train_Softmax(C, dataFile, X, Y, testX, testY, pooledFile, imageDim, fom_func, sgd, save=True, prefix=""):

    if sgd:
        raise NotImplementedError
    else:
        SFC = SoftMaxClassifier(X.T, Y, LAMBDA=C, maxiter=10000)
        print SFC._architecture
        sfcFile = "classifiers/%sSoftMax_lambda%e_%s.pkl" % \
        (prefix, C, pooledFile.split("/")[-1].split(".")[0])

    try:
        print "[*] trained classifier found."
        #SFC = SoftMaxClassifier(X.T, Y, saveFile=sfcFile)
        SFC = pickle.load(open(sfcFile, "rb"))
        print "[*] trained classifier loaded."
    except IOError:
        print "[*] Training Softmax Classifier with LAMBDA=%e" % (C)
        SFC.train()
        print "[+] classifier trained."
        if save:
            print "[+] saving classifier"
            SFC._input = None
            SFC._targets = None
            pickle.dump(SFC, open(sfcFile, "wb"))
            #SFC.saveNetwork(sfcFile)

    pred = SFC.predict(testX.T).T
    indices = np.argmax(pred, axis=1)
    pred = np.max(pred, axis=1)
    pred[indices==0] = 1 - pred[indices==0]
    
    FoM, threshold = fom_func(testY, pred)
    print "[+] FoM: %.4f" % (FoM)
    print "[+] threshold: %.4f" % (threshold)
    
    return FoM, threshold

def cross_validate_Softmax(dataFile, X, Y, m, pooledFile, imageDim, fom_func, n_folds=5):
    
    from sklearn.cross_validation import KFold
    global folds
    X = X.T
        
    CGrid = [30,10,3,1,0.3,0.1,3e-2,1e-2,3e-3,1e-3]
    #CGrid = [30,10]
    kf = KFold(m, n_folds=n_folds)
    taskList = []
    cpu_count = multiprocessing.cpu_count()
    folds = {}
    fold = 1
    FoMs = []
    for train, test in kf:        
        """
        trainX = convert_to_sharedmem(np.ascontiguousarray(X[:,train]))
        trainY = convert_to_sharedmem(np.ascontiguousarray(Y[train]))
        testX  = convert_to_sharedmem(np.ascontiguousarray(X[:,test]))
        testY  = convert_to_sharedmem(np.ascontiguousarray(Y[test]))
        """ 

        trainX = np.concatenate((np.ones(np.shape(X[:,train])[1])[np.newaxis], X[:,train]), axis=0)
        trainY = Y[train]
        testX  = np.concatenate((np.ones(np.shape(X[:,test])[1])[np.newaxis], X[:,test]), axis=0)
        testY  = Y[test]

        folds[fold] = {"X":trainX, \
                       "Y":trainY, \
                       "testX":testX, \
                       "testY":testY}
        fold += 1

    X = None
    Y = None
    for C in CGrid:
        for fold in folds.keys():
            """
            taskList.append(train_SoftMax_task(C, fold, folds[fold]["X"][0], folds[fold]["Y"][0], \
                                               folds[fold]["testX"][0], folds[fold]["testY"][0], \
                                               folds[fold]["X"][1], folds[fold]["Y"][1], \
                                               folds[fold]["testX"][1], folds[fold]["testY"][1], \
                                               fom_func=fom_func))
            """
            """
            taskList.append(train_SoftMax_task(C, fold, folds[fold]["X"], folds[fold]["Y"], \
                                               folds[fold]["testX"], folds[fold]["testY"], \
                                               fom_func=fom_func))
            """
            taskList.append(train_SoftMax_task(C, fold, fom_func=fom_func))
    resultsList = multiprocessingUtils.multiprocessTaskList(taskList, cpu_count)

    FoMs = np.zeros((len(CGrid), n_folds))

    for result in resultsList:
        #print result
        FoMs[CGrid.index(result[2]), result[3]-1] += result[0]
    print np.mean(FoMs, axis=1)
    best_FoM_index = np.argmin(np.mean(FoMs, axis=1))
    print "[+] Best performing classifier: C : %lf" % CGrid[best_FoM_index]
    return CGrid[best_FoM_index]
"""
def convert_to_sharedmem(S):
    size = S.size
    shape = S.shape
    S.shape = size
    S_ctypes = sharedctypes.RawArray('d', S)
    S = np.frombuffer(S_ctypes, dtype=np.float64, count=size)
    S.shape = shape
    return S,shape
"""

def main():
    """
       add -v argument to visualise learned features
    """
    parser = optparse.OptionParser("[!] usage: python convolutional_sparseFiltering.py\n"+\
                                   "\t -F <data file>\n"+\
                                   "\t -P <patches file>\n"+\
                                   "\t -d <image dimension>\n"+\
                                   "\t -c <number of image channels>\n"+\
                                   "\t -p <patch dimension>\n"+\
                                   "\t -f <number of features to learn>\n"
                                   "\t -r <receptive field dimension>\n"+\
                                   "\t -s <step size>\n"+\
                                   "\t -C <regularisation parameter>\n"+\
                                   "\t -V <cross validate>\n"+\
                                   "\t -n <maximum number of patches to use>\n"+\
                                   "\t -m <maximum number of iterations [default=100]>\n"+\
                                   "\t -g <stochastic gradient decent>")
                                   
    parser.add_option("-F", dest="dataFile", type="string", \
                      help="specify data file to analyse")
    parser.add_option("-P", dest="patchesFile", type="string", \
                      help="specify patches file")
    parser.add_option("-d", dest="imageDim", type="int", \
                      help="specify dimension of images in data file")
    parser.add_option("-c", dest="imageChannels", type="int", \
                      help="specify number of channels for images in data file")
    parser.add_option("-p", dest="patchDim", type="int", \
                      help="specify dimension of patches in patches file")
    parser.add_option("-f", dest="numFeatures", type="int", \
                      help="specify number of features for sparse filtering")
    parser.add_option("-r", dest="poolDim", type="int", \
                      help="specify dimension of (pooling dimesion)")
    parser.add_option("-s", dest="stepSize", type="int", \
                      help="specify step size for convolution and pooling")
    parser.add_option("-C", dest="C", type="float", \
                      help="specify the regularisation parameter for linear SVM")
    parser.add_option("-V", action="store_true", dest="cv", \
                      help="specify whether to cross validate [default=False]")
    parser.add_option("-n", dest="numPatches", type="int", \
                      help="specify the maximum number of patches to use [optional]")
    parser.add_option("-m", dest="maxiter", type="int", \
                          help="specify the maximum number iterations [default=100]")
    parser.add_option("-g", action="store_true", dest="sgd", \
                      help="specify whether to use stochastic gradient decent [default=False]")


    (options, args) = parser.parse_args()       
    
    dataFile = options.dataFile
    patchesFile = options.patchesFile
    imageDim = options.imageDim
    imageChannels = options.imageChannels
    patchDim = options.patchDim
    numFeatures = options.numFeatures
    poolDim = options.poolDim
    stepSize = options.stepSize
    C = options.C
    cv = options.cv
    numPatches = options.numPatches
    maxiter = options.maxiter
    sgd = options.sgd
    
    required_arguments = [dataFile, patchesFile, imageDim, imageChannels, \
                 patchDim, numFeatures, poolDim]
                 
    if None in required_arguments:
        print parser.usage
        exit(0)
        
    try:
        assert (numFeatures%stepSize) == 0
    except AssertionError:
        print "[!] Exiting: step size must be a multiple of the number of features."
        exit(0)

    try:
        data = sio.loadmat(patchesFile)
        patches = data["patches"].T[:,:numPatches]
    except IOError:
        print "[!] Exiting: could not open patches file - %s" % patchesFile
        exit(0)
    
    if maxiter == None:
        maxiter = 100
    SF = get_sparseFilter(numFeatures, patches, patchesFile, maxiter=maxiter)
    W = np.reshape(SF.trainedW, (SF.k, SF.n), order="F")
    SF = None
    patches = None
    # added maxiter to filename  24/02/15
    featuresFile = "features/SF_maxiter%d_L1_%s_%dx%d_k%d_%s_pooled%d.mat" % \
    (maxiter, dataFile.split("/")[-1].split(".")[0], patchDim, patchDim, numFeatures, \
    patchesFile.split("/")[-1].split(".")[0], poolDim)
    try:
        features = sio.loadmat(featuresFile)
        pooledFeaturesTrain = features["pooledFeaturesTrain"]
        pooledFeaturesTest = features["pooledFeaturesTest"]
        print "[*] convolved and pooled features loaded"
    except IOError:
        print "[*] no convloved and pooled features found for %s" % dataFile.split("/")[-1]
        print "[+] convolving and pooling..."
        convolve_and_pool(dataFile, featuresFile, W, imageDim, patchDim, poolDim, \
                          numFeatures, stepSize)
        features = sio.loadmat(featuresFile)
        pooledFeaturesTrain = features["pooledFeaturesTrain"]
        pooledFeaturesTest = features["pooledFeaturesTest"]
        
        print "[+] Done."

    if cv == None:
        cv = False

    if sgd == None:
        sgd = False

    trainImages, trainLabels, numTrainImages,\
    testImages, testLabels, numTestImages = load_data(dataFile, imageDim)
        
    trainImages = None
    testImages  = None
        
    X = np.transpose(pooledFeaturesTrain, (0,2,3,1))
    X = np.reshape(X, (int((pooledFeaturesTrain.size)/float(numTrainImages)), \
                   numTrainImages), order="F")
    pooledFeaturesTrain = None
    # MinMax scaling removed 11-03-2015
    scaler = preprocessing.MinMaxScaler()
    scaler.fit(X.T)  # Don't cheat - fit only on training data
    X = scaler.transform(X.T)
    Y = np.squeeze(trainLabels)
        

    testX = np.transpose(pooledFeaturesTest, (0,2,3,1))
    testX = np.reshape(testX, (int((pooledFeaturesTest.size)/float(numTestImages)), \
                       numTestImages), order="F")
    pooledFeaturesTest = None
    # MinMax scaling removed 11-03-2015
    testX = scaler.transform(testX.T)
    testY = np.squeeze(testLabels)

    trainLabels = None
    testLabels  = None


    if C != None and cv == False:

        train_Softmax(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, one_percent_mdr, \
                sgd, save=True, prefix="")

    elif cv == True:
    
        C = cross_validate_Softmax(dataFile, X, Y, numTrainImages, featuresFile, imageDim, one_percent_mdr)
        train_Softmax(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, one_percent_mdr, \
                      sgd, save=True, prefix="")


if __name__ == "__main__":
    main()
