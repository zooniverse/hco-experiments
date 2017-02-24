import sys, pickle
import numpy as np
import scipy.io as sio
from sklearn import svm

def train_SVM(X, y, kernel, C, gamma):
    
    svc = svm.SVC(kernel=kernel, \
                  C=C, \
                  gamma=gamma,
                  probability=True)

    svc.fit(X, y)

    return svc
    

def main(argv = None):
    
    if argv is None:
        argv = sys.argv
    
    if len(argv) != 5:
        sys.exit("Usage: train_SVM.py <kernel> <C>" +\
                 " <gamma> <.mat file>")

    kernel = argv[1]
    C = float(argv[2])
    gamma = float(argv[3])
    dataFile = argv[4]

    data = sio.loadmat(dataFile)

    #train_x = np.concatenate((data["X"], data["validX"]))
    #train_y = np.squeeze(np.concatenate((data["y"], data["validy"])))
    train_x = data["X"]
    train_y = np.squeeze(data["y"])

    svm = train_SVM(train_x, train_y, kernel, C, gamma)

    outputFile = open("SVM_kernel"+str(kernel)+\
                      "_C"+str(C)+\
                      "_gamma"+str(gamma)+\
                      "_"+dataFile.split("/")[-1].split(".")[0]+".pkl", "wb")

    pickle.dump(svm, outputFile)

if __name__ == "__main__":
    main()
