import optparse, pickle
import numpy as np
import scipy.io as sio
from train_SVM import train_SVM
from analyse_SVM import measure_FoM
from sklearn import svm
from sklearn.cross_validation import KFold

def main():

    parser = optparse.OptionParser("[!] usage: python cross_validate_SVM.py -F <data file>")

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
    y = np.squeeze(data["y"])

    kernel_grid = ["rbf"]
    C_grid = [5]
    gamma_grid = [1]

    kf = KFold(m, n_folds=5)
    fold = 1
    for kernel in kernel_grid:
        for C in C_grid:
            for gamma in gamma_grid:
                fold=1
                FoMs = []
                for train, test in kf:
                    print "[*]", fold, kernel, C, gamma
                    file = "cv/SVM_kernel"+str(kernel)+"_C"+str(C)+\
                           "_gamma"+str(gamma)+"_"+dataFile.split("/")[-1].split(".")[0]+\
                           "_fold"+str(fold)+".pkl"
                    try:
                        svm = pickle.load(open(file,"rb"))
                    except IOError:
                        train_x, train_y = X[train], y[train]
                        svm = train_SVM(train_x, train_y, kernel, C, gamma)
                        outputFile = open(file, "wb")
                        pickle.dump(svm, outputFile)
                    FoM, threshold = measure_FoM(X[test], y[test], svm, False)
                    fold+=1
                    FoMs.append(FoM)
                print "[+] mean FoM: %.3lf" % (np.mean(np.array(FoMs)))
                print

if __name__ == "__main__":
    main()
