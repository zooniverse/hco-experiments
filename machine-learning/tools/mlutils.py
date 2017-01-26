#########################################################
# Machine Learning functions and classes - DEW 24/02/15 #
#########################################################

# Imports for ML code - DEW 24/02/15
try:
    import cPickle as pickle
except:
    import pickle

import pyfits, time
import numpy as np
import scipy.io as sio
import scipy.signal as sig
from sklearn import preprocessing
try:
    from sparseFilter import SparseFilter
except ImportError, e:
    print e

def getClassifier():
    """
        clfFile : name of pickled sklearn classifier object.
    """
    path = "/Users/dew/development/PS1-Real-Bogus/ufldl/sparsefiltering/classifiers/"
    clfFile = "SVM_linear_C0.010000_SF_maxiter100_L1_3pi_20x20_skew2_signPreserveNorm_test_no_prescaling_6x6_k400_patches_naturalImages_6x6_signPreserveNorm_pooled5.pkl"
    clf = pickle.load(open(path+clfFile, "rb"))
    return clf

def getScaler(dataFile):
    path = "/Users/dew/development/PS1-Real-Bogus/ufldl/sparsefiltering/scalers/"
    scalerFile = "scaler_%s.pkl" % (dataFile.split("/")[-1].split(".")[0])
    try:
        scaler = pickle.load(open(scalerFile, "rb"))
    except IOError:
        data = sio.loadmat(dataFile)
        try:
            X = np.concatenate((data["X"], data["validX"]))
        except KeyError:
            X = data["X"]
        scaler = preprocessing.StandardScaler(with_std=False).fit(X)
    return scaler

def getMinMaxScaler(featuresFile):
    path = "/Users/dew/development/PS1-Real-Bogus/ufldl/sparsefiltering/scalers/"
    scalerFile = "minMax_scaler_%s.pkl" % (featuresFile.split("/")[-1].split(".")[0])
    try:
        scaler = pickle.load(open(scalerFile, "rb"))
    except IOError:
        features = sio.loadmat(featuresFile)
        pooledFeaturesTrain = features["pooledFeaturesTrain"]
        numTrainImages = np.shape(pooledFeaturesTrain)[1]
        X = np.transpose(pooledFeaturesTrain, (0,2,3,1))
        X = np.reshape(X, (int((pooledFeaturesTrain.size)/float(numTrainImages)), \
                           numTrainImages), order="F")
        scaler = preprocessing.MinMaxScaler()
        scaler.fit(X.T)
    return scaler


def getPatches(patchesFile):
    return sio.loadmat(patchesFile)

def getSparseFilter(numFeatures, patches, patchesFile, maxiter=100):
    try:
        # added maxiter to filename 24/02/15
        path = "/Users/dew/development/PS1-Real-Bogus/ufldl/sparsefiltering/trained_sparseFilters/"
        sf_file = "SF_%d_%s_maxiter%d.mat" % \
        (numFeatures, patchesFile.split("/")[-1].split(".")[0], maxiter)
        #print path+sf_file
        SF = SparseFilter(saveFile=path+sf_file)
        #print "[*] Trained sparse filter loaded."
    except IOError:
        print "[*] Could not find trained sparse filter."
        #print "[+] Training sparse filter ... "
        SF = SparseFilter(k=numFeatures, maxiter=maxiter)
        SF.fit(patches)
        SF.saveSF(path+sf_file)
        #print "[+] Sparse filter trained"
        #SF.visualiseLearnedFeatures()
    return SF

class TargetImage(object):
    
    def __init__(self, fitsFile, extent=10, extension=1):
        """
            fitsFile: name of File from which to extract the image of the object
            
            The image should be already centred on the object of interest, so can
            find its position by accesing the centre of the array of pixel data.
            The image must also be fpacked as recieved from the postage stamp
            server which means the data is in hdulist extension 1. If the image is
            funpacked the hdulist extension is 0.
            
            self.image: a 2*extent x 2*extent np.array of pixel data centreed on the object
            """
        self.fitsFile = fitsFile.split("/")[-1]
        self.objectID = self.fitsFile.split("_")[0]
        self.extent = extent
        pathAndFitsFile = fitsFile
        hdulist = pyfits.open(pathAndFitsFile)
        data = hdulist[extension].data # think this reads in x and y opposite to ds9 see docs
        maxX = np.shape(data[0])
        maxY = np.shape(data[1])
        imageCentre = (maxX[0]/2, maxY[0]/2) # changed to int division, to avoid deprecation warning - DEW 24/02/15
        self.image = data[imageCentre[0]-extent: imageCentre[0]+extent, imageCentre[0]-extent: imageCentre[0]+extent]
    
    def getImage(self):
        return self.image
    
    def getObjectFile(self):
        return self.fitsFile
    
    def signPreserveNorm(self):
        """
            This is a sign preserving nomalisation used in Eye.
            Similar to that used by Romano et al. in SVM paper
            except they use log(1+|x|) i.e. don't divide by sigma.
            nomalizes the unraveled image
            
            vectorized on 24/07/13
            """
        #shape = np.shape(self.getObject())
        Vec = np.nan_to_num(np.ravel(self.getImage(), order="F"))
        #normVec = np.zeros((np.shape(Vec)))
        std = np.std(Vec)
        #for i in range(len(Vec)):
        #    # log1p returns the natural log of (1+x)x
        #    normVec[i] += ((Vec[i])/ np.abs(Vec[i]))*(np.log1p(np.abs(Vec[i])/std))
        #    #print normVec[i]
        normVec = ((Vec)/ np.abs(Vec))*(np.log1p(np.abs(Vec)/std))
        return normVec

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

def convolve_and_pool(images, W, imageDim, patchDim, poolDim, numFeatures, stepSize):
    numImages = np.shape(images)[3]
    pooledFeatures = np.zeros((numFeatures,numImages, \
                               int(np.floor((imageDim-patchDim+1)/poolDim)), \
                               int(np.floor((imageDim-patchDim+1)/poolDim))))
        
    for convPart in range(numFeatures/stepSize):
        featureStart = convPart*stepSize
        featureEnd = (convPart+1)*stepSize
        Wt = W[featureStart:featureEnd, :]
        convolvedFeaturesThis = convolve(patchDim, stepSize, images, Wt)
        pooledFeaturesThis = pool(poolDim, convolvedFeaturesThis)
        pooledFeatures[featureStart:featureEnd, :, :, :] += pooledFeaturesThis
        convolvedFeaturesThis = pooledFeaturesThis = None
    return pooledFeatures
