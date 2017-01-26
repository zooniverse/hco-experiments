import optparse, pickle, warnings
import numpy as np
import scipy.io as sio
from train_nn import train_nn
#from analyse_NN import measure_FoM
from NeuralNet import NeuralNet
#from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import KFold
from sklearn.metrics import f1_score
from sklearn import preprocessing

np.seterr(all="ignore")
def main():

    parser = optparse.OptionParser("[!] usage: python cross_validate_RF.py -F <data file>")

    parser.add_option("-F", dest="dataFile", type="string", \
                      help="specify data file to analyse")

    (options, args) = parser.parse_args()
    dataFile = options.dataFile

    if dataFile == None:
        print parser.usage
        exit(0)

    data = sio.loadmat(dataFile)

    X = data["X"]
    m,n = np.shape(X)
    y = data["y"].T

    arch_grid = [10,20,50,100,200]
    lambda_grid = [10,3,1,.3,.1,.03,.01]


    #kf = StratifiedKFold(np.squeeze(y), n_folds=3, indices=False)
    kf = KFold(m, n_folds=5, indices=False)
    #fold = 1
    for arch in arch_grid:
        for LAMBDA in lambda_grid:
            fold=1
            FoMs = []
            for train, test in kf:
                train_x, train_y = X[train], y[train]
                scaler = preprocessing.StandardScaler().fit(train_x)
                train_x = scaler.transform(train_x)
                print "[*]", fold, arch, LAMBDA
                file = "cv/NeuralNet_"+dataFile.split("/")[-1].split(".")[0]+\
                       "_arch"+str(arch)+"_lambda%.6f"% (LAMBDA) +"_fold"+str(fold)+".pkl"
                try:
                    nn = pickle.load(open(file,"rb"))
                    #nn = NeuralNet(train_x.T, train_y.T, saveFile=file)
                    #print nn._architecture
                    #print nn._trainedParams
                except IOError:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        nn = train_nn(train_x.T, train_y.T, {1:arch}, LAMBDA)
                    outputFile = open(file, "wb")
                    pickle.dump(nn, outputFile)
                #FoM, threshold = measure_FoM(X[test].T, y[test], nn, False)
                FoM = f1_score(y[test], np.array(nn.predict_proba(scaler.transform(X[test]).T) <= .5)[:,0])
                fold+=1
                FoMs.append(FoM)
            print "[+] mean FoM: %.3lf" % (np.mean(np.array(FoMs)))
            print

if __name__ == "__main__":
    main()
