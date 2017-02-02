import numpy as np
import scipy.io as sio
import cPickle as pickle

from pymongo import MongoClient
from swap import SWAP, get_subjects_by_date_limits
from SNHunters_analysis import get_date_limits_from_manifest

def split_subjects_on_magnitude(db, subjects):
    # create a dictionary mapping magnitudes to subjects
    collection = db["metadata"]
    mag_bin_to_subjects_map = {}
    for mag in range(12,23):
        mag_bin_to_subjects_map[mag] = []
    
    for subject_id in subjects:
        #print subject_id
        try:
            mag = collection.find({"subject_id":subject_id})[0]["mag"]
        except IndexError:
            #print subject_id
            continue
        #print mag
        mag_bin_to_subjects_map[int(mag)].append(subject_id)
    return mag_bin_to_subjects_map

def main():
    
    client = MongoClient()
    db = client.SNHunters
    
    mjd_limits = get_date_limits_from_manifest("../data/20160725.txt")
    min_mjd = mjd_limits[0]
    mjd_limits = get_date_limits_from_manifest("../data/20160829.txt")
    max_mjd = mjd_limits[1]
    mjd_limits = (min_mjd, max_mjd)
    print mjd_limits
    #subjects = get_subjects_by_date_limits(db, mjd_limits)
    
    subjects = np.squeeze(sio.loadmat("swap_20160725-20160829.mat")["subjects"]).tolist()
    ids = np.squeeze(sio.loadmat("swap_20160725-20160829.mat")["ids"]).tolist()

    mag_bin_to_subjects_map = split_subjects_on_magnitude(db, subjects)

    out = open("mag_bin_to_subjects_map_20160725-20160829.pkl","wb")
    pickle.dump(mag_bin_to_subjects_map,out)
    out.close()
    
    mag_bin_to_subjects_map = \
        pickle.load(open("mag_bin_to_subjects_map_20160725-20160829.pkl","rb"))
 
    #Run separate swap instances for each magnitude bin.

    #### 13 <= mag < 19
    subjects = mag_bin_to_subjects_map[13] + mag_bin_to_subjects_map[14] + \
               mag_bin_to_subjects_map[15] + mag_bin_to_subjects_map[16] + \
               mag_bin_to_subjects_map[17] + mag_bin_to_subjects_map[18]

    swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)
    swap.process()
    swap.save("swap_20160725-20160829_13-18.mat")

    #### 19 <= mag < 20
    subjects = mag_bin_to_subjects_map[19]

    swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)
    swap.process()
    swap.save("swap_20160725-20160829_19.mat")

    #### 20 <= mag < 21
    subjects = mag_bin_to_subjects_map[20]

    swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)
    swap.process()
    swap.save("swap_20160725-20160829_20.mat")

    #### 21 <= mag < 23
    subjects = mag_bin_to_subjects_map[21] + mag_bin_to_subjects_map[22]

    swap = SWAP(db, subjects, p0=0.1, epsilon=0.5)
    swap.process()
    swap.save("swap_20160725-20160829_21-22.mat")

if __name__ == "__main__":
    main()
