import optparse
import pickle, sys
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from sklearn import svm
from sklearn.metrics import roc_curve

def measure_FoM(X, y, classifier, plot=True):
    pred = classifier.predict_proba(X)[:,1]
    fpr, tpr, thresholds = roc_curve(y, pred)

    FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
    print "[+] FoM: %.4f" % (FoM)
    threshold = thresholds[np.where(fpr<=0.01)[0][-1]]
    print "[+] threshold: %.4f" % (threshold)
    print

    if plot:
        font = {"size": 18}
        plt.rc("font", **font)
        plt.rc("legend", fontsize=14)
    
        plt.xlabel("Missed Detection Rate (MDR)")
        plt.ylabel("False Positive Rate (FPR)")
        plt.yticks([0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0])
        plt.ylim((0,1.05))

        plt.plot(1-tpr, fpr, "k-", lw=5)
        plt.plot(1-tpr, fpr, color="#FF0066", lw=4)

        plt.plot([x for x in np.arange(0,FoM+1e-3,1e-3)], \
                  0.01*np.ones(np.shape(np.array([x for x in np.arange(0,FoM+1e-3,1e-3)]))), \
                 "k--", lw=3)

        plt.plot(FoM*np.ones((11,)), [x for x in np.arange(0,0.01+1e-3, 1e-3)], "k--", lw=3)

        plt.xticks([0, 0.05, 0.10, 0.25, FoM], rotation=70)

        locs, labels = plt.xticks()
        plt.xticks(locs, map(lambda x: "%.3f" % x, locs))
        plt.show()
    return FoM, threshold

def main():

    parser = optparse.OptionParser("[!] usage: python analyse_SVM.py -F <data file>"+\
                                   " -c <classifier file> -s <data set>")

    parser.add_option("-F", dest="dataFile", type="string", \
                      help="specify data file to analyse")
    parser.add_option("-c", dest="classifierFile", type="string", \
                      help="specify classifier to use")
    parser.add_option("-s", dest="dataSet", type="string", \
                      help="specify data set to analyse ([training] or [test] set)")

    (options, args) = parser.parse_args()
    dataFile = options.dataFile
    classifierFile = options.classifierFile
    dataSet = options.dataSet

    print

    if dataFile == None or classifierFile == None or dataSet == None:
        print parser.usage
        exit(0)

    if dataSet != "training" and dataSet != "test":
        print "[!] Exiting: data set must be 1 of 'training' or 'test'"
        exit(0)

    try:
        data = sio.loadmat(dataFile)
    except IOError:
        print "[!] Exiting: %s Not Found" % (dataFile)
        exit(0)

    if dataSet == "training":
        X = data["X"]
        y = np.squeeze(data["y"])
    elif dataSet == "test":
        X = data["testX"]
        y = np.squeeze(data["testy"])

    try:
        classifier = pickle.load(open(classifierFile, "rb"))
    except IOError:
        print "[!] Exiting: %s Not Found" % (classifierFile)
        exit(0)
    measure_FoM(X, y, classifier)

if __name__ == "__main__":
    main()
