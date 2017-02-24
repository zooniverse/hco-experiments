import sys, pickle, warnings
import numpy as np
import scipy.io as sio
from NeuralNet import NeuralNet
from sklearn import preprocessing

def train_nn(train_x, train_y, arch, LAMBDA):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nn = NeuralNet(train_x, train_y, architecture=arch, LAMBDA=LAMBDA, maxiter=10000)
        print nn._architecture
        nn.train()
    return nn

def main(argv = None):

    if argv is None:
        argv = sys.argv

    if len(argv) != 4:
        sys.exit("Usage: train_nn.py <architecture> <lambda> <.mat file>")

    arch = int(argv[1])
    LAMBDA = float(argv[2])
    dataFile = argv[3]

    arch = {1:arch}

    data = sio.loadmat(dataFile)

    #train_x = np.concatenate((data["X"], data["validX"]))            
    #train_y = np.squeeze(np.concatenate((data["y"], data["validy"])))                                                                     
    train_x = data["X"]
    scaler = preprocessing.StandardScaler().fit(train_x)
    train_x = scaler.transform(train_x).T
    train_y = data["y"]
    nn = train_nn(train_x, train_y, arch, LAMBDA)
    outputFile = open("NerualNet_%s_arch%d_lambda%f.pkl" % \
                      (dataFile.split("/")[-1].split(".")[0], arch[1], LAMBDA), "wb")

    pickle.dump(nn, outputFile)

if __name__ == "__main__":
    main()
