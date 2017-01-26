#import pickle
import optparse
import numpy as np
import scipy.io as sio
import scipy.signal as sig
from sparseFilter import SparseFilter
from NeuralNet import SoftMaxClassifier
from SoftMaxOnline import SoftMaxOnline
from sklearn import svm
from sklearn.metrics import roc_curve
from sklearn import preprocessing

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
    SF.visualiseLearnedFeatures()
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

    for convPart in range(numFeatures/stepSize):
        featureStart = convPart*stepSize
        featureEnd = (convPart+1)*stepSize
        print 'Step %d: features %d to %d\n'% (convPart, featureStart, featureEnd)
        Wt = W[featureStart:featureEnd, :]
        #print np.shape(Wt)
        print 'Convolving and pooling train images\n'
        convolvedFeaturesThis = convolve(patchDim, stepSize, trainImages, Wt)
        #convolvedFeaturesThis = convolve(patchDim, stepSize, trainImages, Wt, bt, ZCAWhite, meanPatch)
        pooledFeaturesThis = pool(poolDim, convolvedFeaturesThis)
        pooledFeaturesTrain[featureStart:featureEnd, :, :, :] += pooledFeaturesThis
        convolvedFeaturesThis = pooledFeaturesThis = None
        if np.any(testImages):
            print 'Convolving and pooling test images\n'
            convolvedFeaturesThis = convolve(patchDim, stepSize, testImages, Wt)
            #convolvedFeaturesThis = convolve(patchDim, stepSize, testImages, Wt, bt, ZCAWhite, meanPatch)
            pooledFeaturesThis = pool(poolDim, convolvedFeaturesThis)
            pooledFeaturesTest[featureStart:featureEnd, :, :, :] += pooledFeaturesThis
            convolvedFeaturesThis = pooledFeaturesThis = None

    if np.any(testImages):
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain, \
                     "pooledFeaturesTest":pooledFeaturesTest})
    else:
        sio.savemat(featuresFile, \
                    {"pooledFeaturesTrain":pooledFeaturesTrain})
                 
def train_linearSVM(C, dataFile, X, Y, testX, testY, pooledFile, imageDim, sgd, save=True, prefix=""):

    kernel = "linear"
    C = C

    if sgd:
        from sklearn.linear_model import SGDClassifier
        print "[*] Training linear SVM with stochastic gradient decent alpha=%e" % (C)
        numTrainImages = np.shape(X)[0]
        order = np.random.permutation(numTrainImages)
        X = X[order,:]
        Y = Y[order]
        SVM = SGDClassifier(loss="modified_huber", penalty="l2", alpha=C)
        svmFile = "classifiers/%sSVM_SGD_%s_alpha%e_%s.pkl" % \
        (prefix, kernel, C, pooledFile.split("/")[-1].split(".")[0])
    else:
        SVM = svm.SVC(kernel=kernel, C=C, probability=True)
        svmFile = "classifiers/%sSVM_%s_C%e_%s.pkl" % \
        (prefix, kernel, C, pooledFile.split("/")[-1].split(".")[0])

    #SVM.fit(X, Y)

    try:
        SVM = pickle.load(open(svmFile, "rb"))
        print "[*] trained classifier found."
        print "[*] trained classifier loaded."
    except IOError:
        print "[*] Training linear SVM with C=%e" % (C)
        SVM.fit(X, Y)
        print "[+] classifier trained."
        if save:
            print "[+] saving classifier"
            pickle.dump(SVM, open(svmFile, "wb"))

    pred = SVM.predict(X)

    acc = pred == Y.T
    acc = np.sum(acc)/float(np.shape(acc)[0])
    print 'Accuracy: %2.3f%%\n'% (acc * 100)
    
    pred = SVM.predict(testX)
    acc = pred == testY.T
    acc = np.sum(acc)/float(np.shape(acc)[0])
    print 'Accuracy: %2.3f%%\n'% (acc * 100)
    pred = SVM.predict_proba(testX)[:,1]

    fpr, tpr, thresholds = roc_curve(testY, pred)
    FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
    print "[+] FoM: %.4f" % (FoM)
    threshold = thresholds[np.where(fpr<=0.01)[0][-1]]
    print "[+] threshold: %.4f" % (threshold)

    return FoM, threshold

def train_Softmax(C, dataFile, X, Y, testX, testY, pooledFile, imageDim, sgd, save=True, prefix=""):

    if sgd:
        raise NotImplementedError
    else:
        SFC = SoftMaxClassifier(X.T, Y, LAMBDA=C, maxiter=10000)
        print SFC._architecture
        sfcFile = "classifiers/%sSoftMax_lambda%e_%s.pkl" % \
        (prefix, C, pooledFile.split("/")[-1].split(".")[0])

    try:
        #SFC = pickle.load(open(sfcFile, "rb"))
        SFC = SoftMaxClassifier(saveFile=sfcFile)
        print "[*] trained classifier found."
        print "[*] trained classifier loaded."
    except IOError:
        print "[*] Training Softmax Classifier with LAMBDA=%e" % (C)
        SFC.train()
        print "[+] classifier trained."
        if save:
            print "[+] saving classifier"
            #pickle.dump(SFC, open(sfcFile, "wb"))
            SFC.saveNetwork(sfcFile)

    #pred = SFC.predict(X.T)
    
    #acc = pred == Y.T
    #acc = np.sum(acc)/float(np.shape(acc)[0])
    #print 'Accuracy: %2.3f%%\n'% (acc * 100)
    
    #pred = SFC.predict(testX.T)
    #acc = pred == testY.T
    #acc = np.sum(acc)/float(np.shape(acc)[0])
    #print 'Accuracy: %2.3f%%\n'% (acc * 100)
    pred = SFC.predict(testX.T).T
    indices = np.argmax(pred, axis=1)
    pred = np.max(pred, axis=1)
    pred[indices==0] = 1 - pred[indices==0]
    
    fpr, tpr, thresholds = roc_curve(testY, pred)
    FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
    print "[+] FoM: %.4f" % (FoM)
    threshold = thresholds[np.where(fpr<=0.01)[0][-1]]
    print "[+] threshold: %.4f" % (threshold)
    
    return FoM, threshold

def train_SoftMaxOnline(C, dataFile, X, Y, testX, testY, pooledFile, imageDim, sgd, save=True, prefix=""):
    
    if sgd:
        SFC = SoftMaxOnline(LAMBDA=C)
        sfcFile = "classifiers/%sSoftMaxOnline_lambda%e_%s.pkl" % \
        (prefix, C, pooledFile.split("/")[-1].split(".")[0])

    else:
        raise NotImplementedError("Online learning only implemented for SoftMaxOnline")
    
    try:
        SFC = pickle.load(open(sfcFile, "rb"))
        print "[*] trained classifier found."
        print "[*] trained classifier loaded."
    except IOError:
        print "[*] Training SoftMaxOnline Classifier with LAMBDA=%e" % (C)
        SFC.fit(X,Y)
        print "[+] classifier trained."
        if save:
            print "[+] saving classifier"
            pickle.dump(SFC, open(sfcFile, "wb"))

    pred = SFC.predict_proba(testX)[:,1]
    print np.shape(pred)
    #indices = np.argmax(pred, axis=1)
    #pred = np.max(pred, axis=1)
    #pred[indices==0] = 1 - pred[indices==0]
    #print np.shape(testY), np.shape(pred)
    fpr, tpr, thresholds = roc_curve(testY, pred)
    FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
    print "[+] FoM: %.4f" % (FoM)
    threshold = thresholds[np.where(fpr<=0.01)[0][-1]]
    print "[+] threshold: %.4f" % (threshold)
    
    return FoM, threshold

def cross_validate_Softmax(dataFile, X, Y, pooledFile, imageDim, sgd, save=True, n_folds=5):
    
    from sklearn.cross_validation import KFold
    
    m = len(np.squeeze(Y))
    CGrid = [0.1, 0.03, 0.01, 0.003, 0.001, 3e-4, 1e-4, 3e-5, 1e-5]
    kf = KFold(m, n_folds=n_folds, indices=False)
    mean_FoMs = []
    for C in CGrid:
        fold = 1
        FoMs = []
        for train, test in kf:
            print "[+] training Softmax: LAMBDA : %e, fold : %d" % (C, fold)
            prefix = "cv/cv_fold%d" % fold
            FoM, threshold = train_Softmax(C, dataFile, X[train], Y[train], X[test], Y[test], \
                                             pooledFile, imageDim, sgd, prefix=prefix)
            FoMs.append(FoM)
            fold += 1
        mean_FoMs.append(np.mean(FoMs))
    
    best_FoM_index = np.argmin(mean_FoMs)
    print "[+] Best performing classifier: C : %lf" % CGrid[best_FoM_index]
    return CGrid[best_FoM_index]

def cross_validate_SoftMaxOnline(dataFile, X, Y, pooledFile, imageDim, sgd, save=True, n_folds=5):
    
    from sklearn.cross_validation import KFold
    
    m = len(np.squeeze(Y))
    CGrid = [10, 3, 1, 0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
    kf = KFold(m, n_folds=n_folds, indices=False)
    mean_FoMs = []
    for C in CGrid:
        fold = 1
        FoMs = []
        for train, test in kf:
            print "[+] training SoftMaxOnline: LAMBDA : %e, fold : %d" % (C, fold)
            prefix = "cv/cv_fold%d" % fold
            FoM, threshold = train_SoftMaxOnline(C, dataFile, X[train], Y[train], X[test], Y[test], \
                                                 pooledFile, imageDim, sgd, prefix=prefix)
            FoMs.append(FoM)
            fold += 1
        mean_FoMs.append(np.mean(FoMs))
    
    best_FoM_index = np.argmin(mean_FoMs)
    print "[+] Best performing classifier: C : %lf" % CGrid[best_FoM_index]
    return CGrid[best_FoM_index]

def cross_validate_linearSVM(dataFile, X, Y, pooledFile, imageDim, sgd, save=True, n_folds=5):

    from sklearn.cross_validation import KFold
    
    m = len(np.squeeze(Y))
    CGrid = [10, 3, 1, 0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
    kf = KFold(m, n_folds=n_folds, indices=False)
    mean_FoMs = []
    for C in CGrid:
        fold = 1
        FoMs = []
        for train, test in kf:
            print "[+] training linear SVM: C : %e, fold : %d" % (C, fold)
            prefix = "cv/cv_fold%d" % fold
            FoM, threshold = train_linearSVM(C, dataFile, X[train], Y[train], X[test], Y[test], \
                                   pooledFile, imageDim, sgd, prefix=prefix)
            FoMs.append(FoM)
            fold += 1
        mean_FoMs.append(np.mean(FoMs))

    best_FoM_index = np.argmin(mean_FoMs)
    print "[+] Best performing classifier: C : %lf" % CGrid[best_FoM_index]
    return CGrid[best_FoM_index]

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
        ### Added scaling 06/01/15 ###
        #n,m = np.shape(patches)
        #means = np.mean(patches, axis=0)
        #means = np.tile(means, (n,1))
        #print np.shape(means)
        #patches = patches - means
        #data = means = None
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
    
    
    if C != None and cv == False:
        trainImages, trainLabels, numTrainImages,\
        testImages, testLabels, numTestImages = load_data(dataFile, imageDim)
    
        trainImages = None
        testImages = None

        X = np.transpose(pooledFeaturesTrain, (0,2,3,1))
        X = np.reshape(X, (int((pooledFeaturesTrain.size)/float(numTrainImages)), \
                       numTrainImages), order="F")
        # MinMax scaling removed 11-03-2015
        scaler = preprocessing.MinMaxScaler()
        scaler.fit(X.T)  # Don't cheat - fit only on training data
        X = scaler.transform(X.T)
        #X = X.T
        Y = np.squeeze(trainLabels)
        print Y

        testX = np.transpose(pooledFeaturesTest, (0,2,3,1))
        testX = np.reshape(testX, (int((pooledFeaturesTest.size)/float(numTestImages)), \
                            numTestImages), order="F")
        # MinMax scaling removed 11-03-2015
        testX = scaler.transform(testX.T)
        testY = np.squeeze(testLabels)
        print testY

        #train_linearSVM(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
        #                sgd, save=True, prefix="")
    
        #train_SoftMaxOnline(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
        #                    sgd, save=True, prefix="")

        train_Softmax(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
                      sgd, save=True, prefix="")

    elif cv == True:
        trainImages, trainLabels, numTrainImages,\
        testImages, testLabels, numTestImages = load_data(dataFile, imageDim)
        
        trainImages = None
        testImages = None
        
        X = np.transpose(pooledFeaturesTrain, (0,2,3,1))
        X = np.reshape(X, (int((pooledFeaturesTrain.size)/float(numTrainImages)), \
                           numTrainImages), order="F")
        # MinMax scaling removed 11-03-2015
        scaler = preprocessing.MinMaxScaler()
        scaler.fit(X.T)  # Don't cheat - fit only on training data
        X = scaler.transform(X.T)
        Y = np.squeeze(trainLabels)
                           
        #C = cross_validate_linearSVM(dataFile, X, Y, featuresFile, imageDim, sgd)
        #C = cross_validate_SoftMaxOnline(dataFile, X, Y, featuresFile, imageDim, sgd)
        C = cross_validate_Softmax(dataFile, X, Y, featuresFile, imageDim, sgd)

        testX = np.transpose(pooledFeaturesTest, (0,2,3,1))
        testX = np.reshape(testX, (int((pooledFeaturesTest.size)/float(numTestImages)), \
                           numTestImages), order="F")
        # MinMax scaling removed 11-03-2015
        testX = scaler.transform(testX.T)
        testY = np.squeeze(testLabels)

        #train_linearSVM(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
        #                sgd, save=True, prefix="")
        #train_SoftmaxOnline(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
        #                    sgd, save=True, prefix="")
        train_Softmax(C, dataFile, X, Y, testX, testY, featuresFile, imageDim, \
                      sgd, save=True, prefix="")


if __name__ == "__main__":
    main()
