import pickle, optparse, sys
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from classify import predict
from sklearn.metrics import roc_curve
from sklearn import preprocessing
import mlutils

def visualiseImages(X, pred, annotate=True):
    
    m, n = np.shape(X)
    
    dim = np.ceil(np.sqrt(m))
    k = int(np.sqrt(n))
    dim = 4
    
    fig = plt.figure(facecolor="k")
    for i in range(m):
        ax = fig.add_subplot(dim, dim, i+1)
        image = np.reshape(X[i,:], (k,k), order="F")
        plt.axis("off")
        ax.imshow(image, interpolation="nearest", cmap="hot")
        if annotate:
            ax.text(1.2, 18, "%.3f" % (pred[i]), color="k", fontweight="bold", fontsize=18)
            ax.text(1, 18.2, "%.3f" % (pred[i]), color="k", fontweight="bold", fontsize=18)
            ax.text(0.8, 18, "%.3f" % (pred[i]), color="k", fontweight="bold", fontsize=18)
            ax.text(1, 17.8, "%.3f" % (pred[i]), color="k", fontweight="bold", fontsize=18)
            ax.text(1, 18, "%.3f" % (pred[i]), color="w", fontweight="bold", fontsize=18)
    plt.show()
    
def profileData(clfFile, X, y, threshold=0.5):
    
    y = np.squeeze(y)
    pred = predict(clfFile, X)
    
    positives = pred[y==1]
    negatives = pred[y==0]
    
    true_pos = np.where(positives >= threshold)[0]
    false_neg = np.where(positives < threshold)[0]
    
    true_neg = np.where(negatives < threshold)[0]
    false_pos = np.where(negatives >= threshold)[0]
    
    return true_pos, false_neg, true_neg, false_pos, pred
    
def main():
    
    parser = optparse.OptionParser("[!] usage: python profiling.py\n"+\
                                   "\t -F <data file>\n"+\
                                   "\t -c <classifier file>\n"+\
                                   "\t -t <threshold [default=0.5]>\n"+\
                                   "\t -s <data set>\n"+\
                                   "\t -l <label>\n"+\
                                   "\t -p <pooled features file [optional]>")
    
    parser.add_option("-F", dest="dataFile", type="string", \
                      help="specify data file to analyse")
    parser.add_option("-c", dest="classifierFile", type="string", \
                      help="specify classifier to use")
    parser.add_option("-t", dest="threshold", type="float", \
                      help="specify decision boundary threshold [default=0.5]")
    parser.add_option("-s", dest="dataSet", type="string", \
                      help="specify data set to analyse (training, test)")
    parser.add_option("-l", dest="label", type="int", \
                      help="specify label [optional]")
    parser.add_option("-p", dest="poolFile", type="string", \
                      help="specify pooled features file [optional]")
                      
    (options, args) = parser.parse_args()
    dataFile = options.dataFile
    classifierFile = options.classifierFile
    threshold = options.threshold
    dataSet = options.dataSet
    label = options.label
    poolFile = options.poolFile

    if dataFile == None or classifierFile == None or dataSet == None:
    	print parser.usage
        exit(0)
        
    if threshold == None:
        threshold = 0.5

    try:
        data = sio.loadmat(dataFile)
    except IOError:
        print "[!] Exiting: %s Not Found" % (dataFile)
        exit(0)
        
    if dataSet == "training":
        X = data["X"]
        try:
            y = np.squeeze(data["y"])
        except KeyError:
            m, n = np.shape(X)
            y = np.zeros((m,))
            y += label
    elif dataSet == "test":
        X = data["testX"]
        y = np.squeeze(data["testy"])
    
    if poolFile != None:
        try:
            #scaler = preprocessing.MinMaxScaler()
            #tmp = sio.loadmat("../ufldl/sparsefiltering/features/SF_maxiter100_L1_md_20x20_skew4_SignPreserveNorm_with_confirmed1_6x6_k400_patches_stl-10_unlabeled_meansub_20150409_psdb_6x6_pooled5.mat")["pooledFeaturesTrain"]
            #tmp = sio.loadmat("../ufldl/sparsefiltering/features/SF_maxiter100_L1_3pi_20x20_skew2_signPreserveNorm_6x6_k400_patches_stl-10_unlabeled_meansub_20150409_psdb_6x6_pooled5.mat")["pooledFeaturesTrain"]
            #tmp = np.transpose(tmp, (0,2,3,1))
            #numTrainImages = np.shape(tmp)[3]
            #tmp = np.reshape(tmp, (int((tmp.size)/float(numTrainImages)), \
            #                 numTrainImages), order="F")
            #print np.shape(tmp)
            #scaler.fit(tmp.T)  # Don't cheat - fit only on training data
            #tmp = None
                                           
            features = sio.loadmat(poolFile)
            #pooledFeaturesTrain = np.concatenate((features["pooledFeaturesTrain"],features["pooledFeaturesTest"] ),axis=1)
            pooledFeaturesTrain = features["pooledFeaturesTrain"]
            X = np.transpose(pooledFeaturesTrain, (0,2,3,1))
            numTrainImages = np.shape(X)[3]
            X = np.reshape(X, (int((pooledFeaturesTrain.size)/float(numTrainImages)), \
                           numTrainImages), order="F")
            scaler = preprocessing.MinMaxScaler()
            scaler.fit(X.T)  # Don't cheat - fit only on training data
            X = scaler.transform(X.T)
            if dataSet == "training":
                pass
            elif dataSet == "test":
                pooledFeaturesTest = features["pooledFeaturesTest"]
                X = np.transpose(pooledFeaturesTest, (0,2,3,1))
                numTestImages = np.shape(X)[3]
                X = np.reshape(X, (int((pooledFeaturesTest.size)/float(numTestImages)), \
                               numTestImages), order="F")
                X = scaler.transform(X.T) 
        except IOError:
            print "[!] Exiting: %s Not Found" % (poolFile)
            exit(0)
        finally:
            features = None
            pooledFeaturesTrain = None
            pooledFeaturesTest = None

    true_pos, false_neg, true_neg, false_pos, pred = \
    profileData(classifierFile, X, y, threshold)
        
    if dataSet == "training":
        X = data["X"]
        try:
            files = data["images"]
        except KeyError:
            try:
                files = data["train_files"]
            except KeyError, e:
                print e
                try:
                    files = data["files"]
                except KeyError, e:
                    print e
                    print "[!] Exiting: Could not load training set from %s" % dataFile
                    exit(0)

    elif dataSet == "test":
        X = data["testX"]
        files = data["test_files"]
    data = None
    m,n = np.shape(X)
    print "[*] %d examples." % (m)
    if label == 1 or 1 in set(y):
        m, n = np.shape(X[y==1,:])
        print m
        print "[*] %d false negatives." % (len(false_neg))
        print "[*] FNR (MDR) = %.3f" % (len(false_neg)/float(m))
        fnX = X[y==1,:][false_neg,:]
        fn_pred = pred[y==1][false_neg]
    
        visualiseImages(fnX[:400], fn_pred[:400], True)
    
    if label == 0 or 0 in set(y):
        m, n = np.shape(X[y==0,:])
        print m
        print "[*] %d false positives." % (len(false_pos))
        print "[*] FPR = %.3f" % (len(false_pos)/float(m))
        fpX = X[y==0][false_pos,:]
        fp_pred = pred[y==0][false_pos]
    
        visualiseImages(fpX[:100], fp_pred[:100], True)

    positives = files[y==1]
    negatives = files[y==0]
    print "[+] Missed Detection files :"
    for index in false_neg:
        print str(positives[index]).rstrip()
    print
    print "[+] False Positive files :"
    for index in false_pos:
        print str(negatives[index]).rstrip()
    

if __name__ == "__main__":
    main()
