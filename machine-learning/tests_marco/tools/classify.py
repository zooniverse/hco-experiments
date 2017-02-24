import sys, optparse
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, f1_score
from sklearn import preprocessing
from tests_marco.tools import mlutils
from tests_marco.config import config
import pickle

# config
cfg = config.Config()
data_path = cfg.paths['data']

predictionsPath = data_path + "predictions/"

def one_percent_mdr(y, pred, fom):
    fpr, tpr, thresholds = roc_curve(y, pred)
    FoM = fpr[np.where(1-tpr<=fom)[0][0]] # FPR at 1% MDR
    threshold = thresholds[np.where(1-tpr<=fom)[0][0]]
    return FoM, threshold, fpr, tpr

def one_percent_fpr(y, pred, fom):
    fpr, tpr, thresholds = roc_curve(y, pred)
    FoM = 1-tpr[np.where(fpr<=fom)[0][-1]] # MDR at 1% FPR
    threshold = thresholds[np.where(fpr<=fom)[0][-1]]
    return FoM, threshold, fpr, tpr

def predict(clfFile, X):

    if "SVM" in clfFile or "RF" in clfFile:
        clf = pickle.load(open(clfFile, "rb"))
        pred = clf.predict_proba(X)[:,1]
    elif "SoftMax" in clfFile:
        if "SoftMaxOnline" in clfFile:
            m,n = np.shape(X)
            smoc = pickle.load(open(clfFile, "rb"))
            pred = smoc.predict_proba(X)
            #pred = clf.predict(X.T).T
            indices = np.argmax(pred, axis=1)
            pred = np.max(pred, axis=1)
            pred[indices==0] = 1 - pred[indices==0]
        else:
            clf = pickle.load(open(clfFile, "rb"))
            pred = clf.predict(X.T).T
            indices = np.argmax(pred, axis=1)
            pred = np.max(pred, axis=1)
            pred[indices==0] = 1 - pred[indices==0]
    #print pred
    #print np.median(pred)
    #print np.mean(pred)
    return pred

def hypothesisDist(y, pred, threshold=0.5):

    # the raw predictions for actual garbage
    garbageHypothesis = pred[np.where(y == 0)[0]]
    realHypothesis = pred[np.where(y == 1)[0]]

    font = {"size"   : 26}
    plt.rc("font", **font)
    plt.rc("legend", fontsize=22)
    #plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    #plt.yticks([x for x in np.arange(500,3500,500)])
    bins = [x for x in np.arange(0,1.04,0.04)]

    real_counts, bins, patches = plt.hist(realHypothesis, bins=bins, alpha=1, \
                                          label="real", color="#FF0066", edgecolor="none")
    #plt.hist(realHypothesis, bins=bins, alpha=1, lw=5, color="k", histtype="step")
    #real_counts, bins, patches = plt.hist(realHypothesis, bins=bins, alpha=1, lw=4,\
    #                                      label="real", color="#FF0066", histtype="step")
    print(real_counts)
    garbage_counts, bins, patches = plt.hist(garbageHypothesis, bins=bins, alpha=1, \
                                             label="bogus", color="#66FF33", edgecolor="none")
    #plt.hist(garbageHypothesis, bins=bins, alpha=1,  lw=5, color="k", histtype="step")
    #garbage_counts, bins, patches = plt.hist(garbageHypothesis, bins=bins, alpha=1,  lw=4,\
    #                                         label="bogus", color="#66FF33", histtype="step")

    print(garbage_counts)
    # calculate where the real counts are less than the garbage counts.
    # these are to be overplotted for clarity

    try:
        real_overlap = list(np.where(np.array(real_counts) <= np.array(garbage_counts))[0])
        for i in range(len(real_overlap)):
            to_plot = [bins[real_overlap[i]], bins[real_overlap[i]+1]]
            plt.hist(realHypothesis, bins=to_plot, alpha=1, color="#FF0066", edgecolor="none")
            #plt.hist(realHypothesis, bins=to_plot, alpha=1, color="k", lw=5, histtype="step")
            #plt.hist(realHypothesis, bins=to_plot, alpha=1, color="#FF0066", lw=4, histtype="step")
    except IndexError:
        pass

    max = int(np.max(np.array([np.max(real_counts), np.max(garbage_counts)])))
    print(max)
    decisionBoundary = np.array([x for x in range(0,max,100)])

    if garbage_counts[0] != 0:
        plt.text(0.01, 0.1*garbage_counts[0], str(int(garbage_counts[0])), rotation="vertical", size=22)

    plt.plot(threshold*np.ones(np.shape(decisionBoundary)), decisionBoundary, \
             "k--", label="decision boundary=%.3f"%(threshold), linewidth=2.0)

    y_min = -0.02*int(plt.axis()[-1])
    y_max = plt.axis()[-1]
    plt.xlim(-0.015,1.015)
    plt.ylim(y_min,y_max)
    #plt.title(dataFile.split("/")[-1])
    plt.xlabel("Hypothesis")
    plt.ylabel("Frequency")
    leg = plt.legend(loc="upper center")
    leg.get_frame().set_alpha(0.5)
    plt.show()

def plot_ROC(Ys, preds, fom_func, color="#FF0066", Labels=None):

    fig = plt.figure()
    #font = {"size": 22}
    #plt.rc("font", **font)
    #plt.rc("legend", fontsize=20)

    plt.xlabel("Missed Detection Rate (MDR)")
    plt.ylabel("False Positive Rate (FPR)")
    #
    plt.ylim((0,1.05))
    default_ticks = [0, 0.05, 0.10, 0.25]
    ticks = []

    colours = ["#FF0066", "#66FF33", "#3366FF"]
    #Labels = ["Wright+15", "no normalisation"]

    for j,pred in enumerate(preds):
        y = Ys[j]
        #fpr, tpr, thresholds = roc_curve(y, pred)

        FoMs = []
        decisionBoundaries = []
        if len(preds) == 1:
            foms = [0.01, 0.05, 0.1]
            color="#3366FF"
        else:
            foms = [0.01]
            color = colours[j]
            #label=Labels[j]

        for fom in foms:
            #FoMs.append(1-tpr[np.where(fpr<=FPR)[0][-1]])
            FoM, threshold, fpr, tpr = fom_func(y, pred, fom)
            FoMs.append(FoM)
            decisionBoundaries.append(threshold)

        plt.plot(1-tpr, fpr, "k-", lw=5)
        #color = "#FF0066" # pink
        #color = "#66FF33" # green
        #color = "#3366FF" #blue
        #print label
        if Labels:
            plt.plot(1-tpr, fpr, color=color, lw=4, label=Labels[j])
        else:
            plt.plot(1-tpr, fpr, color=color, lw=4)
        if fom_func == one_percent_fpr:
            for i,FoM in enumerate(FoMs):
                print("[+] FoM at %.3f FPR : %.3f | decision boundary : %.3f " % (foms[i], FoM, decisionBoundaries[i]))
                plt.plot([x for x in np.arange(0,FoM+1e-3,1e-3)], \
                         foms[i]*np.ones(np.shape(np.array([x for x in np.arange(0,FoM+1e-3,1e-3)]))), \
                         "k--", lw=3, zorder=100)

                plt.plot(FoM*np.ones(np.shape([x for x in np.arange(0,foms[i]+1e-3, 1e-3)])), \
                        [x for x in np.arange(0,foms[i]+1e-3, 1e-3)], "k--", lw=3, zorder=100)
                if round(FoM,1) in default_ticks:
                    default_ticks.remove(round(FoM,1))
                    ticks.append(FoM)
                else:
                    ticks.append(FoM)
                plt.xticks(default_ticks+ticks, rotation=70)
                locs, labels = plt.xticks()
                plt.xticks(locs, ["%.3f" % x for x in locs])
                plt.yticks([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0])
        elif fom_func == one_percent_mdr:
            for i,FoM in enumerate(FoMs):
                print("[+] FoM at %.3f MDR : %.3f | decision boundary : %.3f " % (foms[i], FoM, decisionBoundaries[i]))
                plt.plot(foms[i]*np.ones(np.shape(np.array([x for x in np.arange(0,FoM+1e-3,1e-3)]))), \
                         [x for x in np.arange(0,FoM+1e-3,1e-3)], \
                         "k--", lw=3, zorder=100)

                plt.plot([x for x in np.arange(0,foms[i]+1e-3, 1e-3)],\
                         FoM*np.ones(np.shape([x for x in np.arange(0,foms[i]+1e-3, 1e-3)])), \
                         "k--", lw=3, zorder=100)
                if round(FoM,1) in default_ticks:
                    default_ticks.remove(round(FoM,1))
                    ticks.append(FoM)
                else:
                    ticks.append(FoM)
                plt.yticks(default_ticks+ticks, rotation=70)
                locs, labels = plt.yticks()
                plt.yticks(locs, ["%.3f" % x for x in locs])
                plt.xticks([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0])
    if Labels:
        plt.legend()
    #plt.savefig('FoM.pdf', bbox_inches='tight')
    plt.show()

def test_FDR_procedure(y, pred):
    # get all the test cases where the null hypothesis is true
    null_true_pred = pred[y==0]
    # get bins for predicted values
    bins = [x for x in np.arange(0,1+1e-3,1e-3)]
    # determine the counts of true null hypothesis cases in
    # each bin
    counts, bins = np.histogram(null_true_pred, bins=bins)
    # calculate the normalised cumulative sum of the counts in
    # each bin.
    cumsum_norm = np.cumsum(counts) / float(len(null_true_pred))
    cumsum_norm = cumsum_norm.tolist()
    cumsum_norm.insert(0,0)
    cumsum_norm = np.array(cumsum_norm)
    print(cumsum_norm)
    #plt.plot(bins[:-1], cumsum_norm)
    #plt.xlim(xmin=-0.01, xmax=1.01)
    #plt.ylim(ymin=-0.01, ymax=1.01)
    #plt.show()
    # p-values are probability that a test element would
    # be observed in a given bin assuming the null hypothesis
    # is true for that element.
    p_values_per_bin = (1 - cumsum_norm)
    #print p_values_per_bin
    # set alpha the FDR to 0.01
    alpha = 0.01
    # divide the test set into 2 different sized chunks to test the
    # adaptive thresholding.
    pred_chunk_1 = pred
    y_chunk_1 = y
    #print pred_chunk_1
    pred_chunk_2 = pred[-200:]
    y_chunk_2 = y[-200:]
    # get number of tests
    num_tests_chunk_1 = float(len(pred_chunk_1))
    #print num_tests_chunk_1
    # calculate p-values for each example in chunk 1
    indices = np.digitize(pred_chunk_1, bins[:-1])
    # get and sort p-values
    p_vals_chunk_1 = [p_values_per_bin[i-1] for i in indices]
    #zipped = zip(p_vals_chunk_1, y_chunk_1)
    #zipped.sort()
    #p_vals_chunk_1, y_chunk_1 = zip(*zipped)
    p_vals_chunk_1.sort()
    j_alpha_chunk_1 = [j*alpha/num_tests_chunk_1 for j in range(1, int(num_tests_chunk_1)+1)]
    #for j in range(int(num_tests_chunk_1)):
    #    print j*alpha/num_tests_chunk_1
    diff_chunk_1 = np.array(p_vals_chunk_1) - np.array(j_alpha_chunk_1)
    print(diff_chunk_1)
    print(np.where(diff_chunk_1<=0)[0][-1])
    print(diff_chunk_1[np.where(diff_chunk_1<=0)[0][-1]])
    print(p_vals_chunk_1[np.where(diff_chunk_1<=0)[0][-1]])
    threshold = p_vals_chunk_1[np.where(diff_chunk_1<=0)[0][-1]]

    pred_chunk_1 = pred
    y_chunk_1 = y
    y_chunk_1 = np.array(y_chunk_1)
    p_vals_chunk_1 = np.array(p_vals_chunk_1)
    positives = p_vals_chunk_1[np.where(y_chunk_1 == 1)[0]]
    #print positives
    negatives = p_vals_chunk_1[np.where(y_chunk_1 == 0)[0]]
    #print negatives
    print(len(positives))
    print(len(negatives))
    print("MDR : %.3f" % (len(positives[np.where(positives<=threshold)]) / float(len(positives))))
    print("FPR : %.3f" % (len(negatives[np.where(negatives<=threshold)]) / float(len(negatives))))


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def FoM(y, pred, threshold=0.5):
    # the raw predictions for actual garbage
    garbageHypothesis = pred[np.where(y == 0)[0]]
    realHypothesis = pred[np.where(y == 1)[0]]

    fpr, tpr, thresholds = roc_curve(y, pred)

    threshold = find_nearest(thresholds, threshold)
    print(find_nearest(thresholds, threshold))
    print(1-tpr[np.squeeze(np.where(thresholds==threshold))])
    print("[+] FPR: %.3f" % fpr[np.squeeze(np.where(thresholds==threshold))])
    print("[+] FoM: %.3f" % (1-tpr[np.squeeze(np.where(thresholds==threshold))]))

def getUniqueIds(files):

    ids = []
    for file in files:
        ids.append(str(file))
        #ids.append(file.rstrip().split("_")[0])
    return set(ids)

def predict_byName(pred, files, outputFile):

    files = files.tolist()
    ids = getUniqueIds(files)
    predictions_byName = {}
    for id in ids:
        predictions_byName[id] = []
        for file in files:
            if str(file) == id:
                predictions_byName[id].append(pred[files.index(file)])
    output = open(outputFile, "w")
    pred = np.zeros((len(list(predictions_byName.keys()),)))
    for i,key in enumerate(predictions_byName.keys()):
        #print key, np.median(np.array(predictions_byName[key])), len(predictions_byName[key])
        pred[i] += np.median(np.array(predictions_byName[key]))
        output.write(str(key) +"," + str(np.median(np.array(predictions_byName[key]))) + "\n")
    output.close()
    print(len(pred))
    return pred

def labels_byName(files, y):
    files = files.tolist()
    ids = getUniqueIds(files)
    labels_byName = {}
    for id in ids:
        labels_byName[id] = []
        for file in files:
            #if file.rstrip().split("_")[0] == id:
            if str(file) == id:
                labels_byName[id].append(y[files.index(file)])
    labels = np.zeros(np.shape(list(labels_byName.keys())));
    for i,key in enumerate(labels_byName.keys()):
        if not (labels_byName[key] == labels_byName[key][0]).all():
            print(labels_byName[key], np.argmax(np.bincount(labels_byName[key])))
        labels[i] += np.argmax(np.bincount(labels_byName[key]))
    return labels

def round_down(num, divisor):
    return num - (num%divisor)

def generate_Learning_Curve(X, y, classifierFile):

    try:
         assert "SoftMax" in classifierFile
    except AssertionError:
        print("Only implemented for SoftMaxClassifier")

    m, n = np.shape(X)

    print(np.shape(X))
    train_x = X[:.75*m,:]
    train_y = np.squeeze(y[:.75*m])
    print(np.shape(train_x))
    print(np.shape(train_y))

    cv_x =  X[.75*m:,:]
    cv_y =  np.squeeze(y[.75*m:])

    max_step = int(round_down(.75*m, 100))

    m, n = np.shape(train_x)

    steps = list(range(100, max_step+100,100))
    steps.append(m)

    smc = pickle.load(open(classifierFile, "rb"))
    LAMBDA  = smc._LAMBDA
    maxiter = smc._maxiter

    train_FoMs = []
    cv_FoMs    = []

    for step in steps:

        smc = SoftMaxClassifier(train_x[:step,:].T, train_y[:step], LAMBDA=LAMBDA, maxiter=maxiter)
        print(smc._architecture)
        smc.train()
        pred = smc.predict(train_x[:step,:].T).T
        indices = np.argmax(pred, axis=1)
        pred = np.max(pred, axis=1)
        pred[indices==0] = 1 - pred[indices==0]
        fpr, tpr, thresholds = roc_curve(train_y[:step], pred)
        FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
        train_FoMs.append(FoM)
        pred = smc.predict(cv_x.T).T
        indices = np.argmax(pred, axis=1)
        pred = np.max(pred, axis=1)
        pred[indices==0] = 1 - pred[indices==0]
        fpr, tpr, thresholds = roc_curve(cv_y, pred)
        FoM = 1-tpr[np.where(fpr<=0.01)[0][-1]]
        cv_FoMs.append(FoM)

    plt.plot(steps, train_FoMs)
    plt.plot(steps, cv_FoMs)
    plt.show()

def feature_importance(X, classifier, feature_names):
    importances = classifier.feature_importances_
    indices = np.argsort(importances)[::-1]
    std = np.std([tree.feature_importances_ for tree in classifier.estimators_],
                 axis=0)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(list(range(X.shape[1])), importances[indices],
           color="r", yerr=std[indices], align="center")
    ax.set_xticks(list(range(X.shape[1])))
    ax.set_xticklabels(np.array(feature_names)[indices],rotation=70)
    plt.xlim([-1, X.shape[1]])
    #plt.savefig('feature_importances.pdf', bbox_inches='tight')
    plt.show()

def print_misclassified(y, pred, files, fom_func, threshold):

    #fpr, tpr, thresholds = roc_curve(y, pred)

    #fom = 0.01

    #FoMs.append(1-tpr[np.where(fpr<=FPR)[0][-1]])
    #FoM, threshold, fpr, tpr = fom_func(y, pred, fom)
    negatives = np.where(y==0)
    positives = np.where(y==1)

    falsePositives = files[negatives][np.where(pred[negatives]>threshold)]

    print("[+] False positives (%d):" % len(falsePositives))
    for i,falsePositive in enumerate(falsePositives):
        print("\t " + str(falsePositive), pred[negatives][np.where(pred[negatives]>threshold)][i])
    print()
    missedDetections = files[positives][np.where(pred[positives]<=threshold)]
    print("[+] Missed Detections (%d):" % len(missedDetections))
    for i,missedDetection in enumerate(missedDetections):
        print("\t " + str(missedDetection), pred[positives][np.where(pred[positives]<=threshold)][i])
    print()


def main():


    parser = optparse.OptionParser("[!] usage: python classify.py\n"+\
                                   " -F <data files [comma-separated]>\n"+\
                                   " -c <classifier files [comma-separated]>\n"+\
                                   " -t <threshold [default=0.5]>\n"+\
                                   " -s <data set>\n"+\
                                   " -o <output file>\n"+\
                                   " -f <figure of merit [\"fpr\" or \"mdr\"]>"
                                   " -p <plot hypothesis distribution [optional]>\n"+\
                                   " -r <plot ROC curve [optional]>\n"+\
                                   " -n <classify by name [optional]>\n"+\
                                   " -P <pooled features file [optional]>\n"+\
                                   " -L <plot learning curve [optional]>\n"+\
                                   " -l <labels for plotting [optional, comma-separated]>\n"+\
                                   " -m <print miss classified file names>")

    parser.add_option("-F", dest="dataFiles", type="string", \
                      help="specify data file[s] to analyse")
    parser.add_option("-c", dest="classifierFiles", type="string", \
                      help="specify classifier[s] to use")
    parser.add_option("-t", dest="threshold", type="float", \
                      help="specify decision boundary threshold [default=0.5]")
    parser.add_option("-o", dest="outputFile", type="string", \
                      help="specify output file")
    parser.add_option("-f", dest="fom", type="string", \
                      help="specify the figure of merit either 1% FPR or 1% MDR - choose \"fpr\" or \"mdr\"")
    parser.add_option("-s", dest="dataSet", type="string", \
                      help="specify data set to analyse [default=test]")
    parser.add_option("-p", action="store_true", dest="plot", \
                      help="specify whether to plot the hypothesis distribution [optional]")
    parser.add_option("-r", action="store_true", dest="roc", \
                      help="specify whether to plot the ROC curve [optional]")
    parser.add_option("-n", action="store_true", dest="byName", \
                      help="specify whether to classify objects by name [optional]")
    parser.add_option("-P", dest="poolFile", type="string", \
                      help="specify pooled features file [optional]")
    parser.add_option("-L", action="store_true", dest="learningCurve", \
                      help="specify whether to generate a leraning curve [optional]")
    parser.add_option("-l", dest="labels", type="string", \
                      help="specify label[s] for plots [optional]")
    parser.add_option("-m", action="store_true", dest="miss", \
                      help="specify whether or not to print misclassified file names [optional]")

    (options, args) = parser.parse_args()

    ## TODO: Test by defining arguments
    if False:
        cfg = config.Config()
        data_path = cfg.paths['data']

        dataFile = data_path + "3pi_20x20_skew2_signPreserveNorm.mat"
        patchesFile = data_path + "patches_stl-10_unlabeled_meansub_20150409_psdb_6x6.mat"
        imageDim = 20
        imageChannels = 1
        patchDim = 6
        numFeatures = 20
        poolDim = 5
        stepSize = 20



    try:
        dataFiles = options.dataFiles.split(",")
        classifierFiles = options.classifierFiles.split(",")
        threshold = options.threshold
        outputFile = options.outputFile
        fom = options.fom
        dataSet = options.dataSet
        plot = options.plot
        roc = options.roc
        byName = options.byName
        poolFile = options.poolFile
        learningCurve = options.learningCurve
        miss = options.miss
        try:
            labels = options.labels.split(",")
        except:
            labels = None
    except AttributeError as e:
        print(e)
        print(parser.usage)
        exit(0)

    if dataFiles == None or classifierFiles == None:
        print(parser.usage)
        exit(0)

    if threshold == None:
        threshold = 0.5

    if dataSet == None:
        dataSet = "test"

    if fom == "fpr":
        fom_func = one_percent_fpr
    elif fom == "mdr":
        fom_func = one_percent_mdr
    else:
        fom_func = one_percent_fpr


    Xs = []
    Ys = []
    Files = []
    for dataFile in dataFiles:
        data = sio.loadmat(dataFile)
        print("[+] %s" % dataFile)
        X = np.nan_to_num(data["X"])
        #scaler = preprocessing.StandardScaler(with_std=False).fit(X)
        if dataSet == "test":
            try:
                Xs.append(np.nan_to_num(data["testX"]))
                #Xs.append(scaler.transform(data["testX"]))
                Ys.append(np.squeeze(data["testy"]))
                Files.append(data["test_files"])
            except KeyError:
                if plot:
                    y = np.zeros((np.shape(X)[0],))
                else:
                    print("[!] Exiting: Could not load test set from %s" % dataFile)
                    exit(0)
        elif dataSet == "training":
            try:
                Xs.append(np.nan_to_num(data["X"]))
                #Xs.append(np.squeeze(np.concatenate((data["X"], data["testX"]))))
                try:
                    #Ys.append(np.squeeze(np.concatenate((data["y"], data["testy"]))))
                    if -1 in data["y"]:
                        print(np.squeeze(np.where(data["y"] != -1)[1]))
                        Ys.append(np.squeeze(data["y"][np.where(data["y"] != -1)]))
                    else:
                        Ys.append(np.squeeze(data["y"]))
                except KeyError:
                    if fom:
                        print("[!] Exiting: Could not load labels from %s" % dataFile)
                        print("[*] FoM calculation is not possible without labels.")
                        exit(0)
                    else:
                        Ys.append(np.zeros((np.shape(X)[0],)))
                Files.append(data["images"])
            except KeyError:
                try:
                    Files.append(data["train_files"])
                except KeyError as e:
                    print(e)
                    try:
                        Files.append(data["files"])
                    except KeyError as e:
                        print(e)
                        print("[!] Exiting: Could not load training set from %s" % dataFile)
                        exit(0)
        elif dataSet == "all":
            try:
                Xs.append(np.nan_to_num(np.concatenate((data["X"], data["testX"]))))
                try:
                    Ys.append(np.squeeze(np.concatenate((data["y"], data["testy"]))))
                except KeyError:
                    if fom:
                        print("[!] Exiting: Could not load labels from %s" % dataFile)
                        print("[*] FoM calculation is not possible without labels.")
                        exit(0)
                    else:
                        Ys.append(np.zeros((np.shape(Xs[0])[0],)))
                Files.append(np.squeeze(np.concatenate((data["images"], data["test_files"]))))
            except KeyError:
                try:
                    Files.append(np.squeeze(np.concatenate((data["train_files"], data["test_files"]))))
                except KeyError as e:
                    print(e)
                    try:
                        Files.append(np.squeeze(np.concatenate((data["files"], data["test_files"]))))
                    except KeyError as e:
                        print(e)
                        print("[!] Exiting: Could not load training set from %s" % dataFile)
                        exit(0)
        else:
            print("[!] Exiting: %s is not a valid choice, choose one of \"training\" or \"test\"" % dataSet)
            exit(0)


    preds = []
    for classifierFile in classifierFiles:
        dataFile = dataFiles[classifierFiles.index(classifierFile)]
        try:
            predFile = predictionsPath+classifierFile.split("/")[-1].replace(".pkl","")+"_predictions_%s_%s.mat"%(dataFile.split("/")[-1].replace(".mat",""), dataSet)
            preds.append(np.squeeze(sio.loadmat(predFile)["predictions"]))
        except IOError:
            if poolFile != None:
                Xs = []
                try:
                    features = sio.loadmat(poolFile)
                    try:
                        pooledFeaturesTrain = features["pooledFeaturesTrain"]
                    except KeyError:
                        pooledFeaturesTrain = features["pooledFeatures"]

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
                    Xs.append(X)
                except IOError:
                    print("[!] Exiting: %s Not Found" % (poolFile))
                    exit(0)
                finally:
                    features = None
                    pooledFeaturesTrain = None
                    pooledFeaturesTest = None

            X = Xs[classifierFiles.index(classifierFile)]
            if learningCurve:
                y = Ys[classifierFiles.index(classifierFile)]
                generate_Learning_Curve(X, y, classifierFile)
            else:
                pred = predict(classifierFile, X)
                #predFile = predictionsPath+classifierFile.split("/")[-1].replace(".mat","")+"_predictions_%s.mat"%dataSet
                #sio.savemat(predFile,{"ids":Files[classifierFiles.index(classifierFile)],"predictions":pred})
                preds.append(np.squeeze(pred))
    #X = Xs = None

    if outputFile != None and not byName:
        output = open(outputFile, "w")
        files = Files[0]
        pred = preds[0]
        y = Ys[0]
        for i,prediction in enumerate(pred):
            output.write(files[i].rstrip() + "," + str(prediction) + "," + str(y[i]) + "\n")
        output.close()

    if byName:
        files = Files[0]
        pred = preds[0]
        print(pred)
        print(files)
        print(outputFile)
        preds = [predict_byName(pred, files, outputFile)]
        try:
            Ys = [labels_byName(files, Ys[0])]
        except NameError as e:
            print(e)

    if plot:
        try:
            for pred in preds:
                hypothesisDist(Ys[preds.index(pred)], pred, threshold)
        except NameError as e:
            print("[!] NameError : %s", e)

    if roc:
        plot_ROC(Ys, preds, fom_func, Labels=labels)
        #test_FDR_procedure(Ys[0], preds[0])

    clf = pickle.load(open(classifierFiles[0],"rb"))
    if type(clf) == type(RandomForestClassifier()):
        try:
            feature_names = []
            for f in sio.loadmat(dataFiles[0])["features"]:
                feature_names.append(str(f))
            feature_importance(Xs[0], clf, feature_names)
        except KeyError:
            feature_importance(Xs[0], clf, list(range(Xs[0].shape[1])))

    if miss:
        print_misclassified(Ys[0], preds[0], np.squeeze(Files[0]), fom_func, threshold)

if __name__ == "__main__":
    main()
