import sys, pickle
import numpy as np
import scipy.io as sio
from sklearn.ensemble import RandomForestClassifier
from tests_marco.config import config

def train_RF(X, y, n_estimators, max_features, min_samples_leaf):

    rf = RandomForestClassifier(n_estimators=n_estimators, \
                                max_features=max_features, \
                                min_samples_leaf=min_samples_leaf)

    rf.fit(X, y)

    return rf


def main(argv = None):

    cfg = config.Config()
    data_path = cfg.paths['data']

    if argv is None:
        argv = sys.argv

    if len(argv) != 5:
        sys.exit("Usage: train_RF.py <n_estimators> <max_features>" +\
                 " <min_samples_leaf> <.mat file>")

    n_estimators = int(argv[1])
    max_features = int(argv[2])
    min_samples_leaf = int(argv[3])
    dataFile = argv[4]

    # TODO: Remove, only for testing
    if False:
        n_estimators = 100
        max_features = 10
        min_samples_leaf = 1
        dataFile = data_path + "3pi_20x20_skew2_signPreserveNorm.mat"

    data = sio.loadmat(dataFile)

    #train_x = np.concatenate((data["X"], data["validX"]))
    #train_y = np.squeeze(np.concatenate((data["y"], data["validy"])))
    train_x = np.nan_to_num(data["X"])
    train_y = np.squeeze(data["y"])

    rf = train_RF(train_x, train_y, n_estimators, max_features, min_samples_leaf)



    outputFile = open(data_path + "classifiers/RF_n_estimators"+str(n_estimators)+\
                      "_max_features"+str(max_features)+\
                      "_min_samples_leaf"+str(min_samples_leaf)+\
                      "_"+dataFile.split("/")[-1].split(".")[0]+".pkl", "wb")

    pickle.dump(rf, outputFile)

if __name__ == "__main__":
    main()
