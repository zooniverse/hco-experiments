# Analyse Performance of different Users on different Meta-Data Splits
# The underlying assumption of improving SWAP is that different users
# are not equally/linearly better/worse on different meta-data splits

# get data from database
from swap.swap import SWAP
from swap.mongo import DB
from swap.mongo import Query, Group
from swap.config import Config
import time
import numpy as np

# Check data in data base
db = DB()
cfg = Config()
classifications = db.classifications

# get data from db
fields = ["user_name","subject_id","annotation","gold_label","metadata"]
q = Query()
q.project(fields)
dat = classifications.aggregate(q.build(),batchSize=int(1e5))

# save data per user
usr = dict()

# convert to magnitude bin
def mag2bin(val):
    if np.isnan(val):
        return val
    mag_ranges = [(13, 18), (18, 19), (19, 20), (20, 23)]
    bin_val = min([x[1] for x in mag_ranges if val<=x[1]])
    return bin_val

# Loop over all classifications and update
for d in dat:
    user = str(d["user_name"])
    ann = d["annotation"]
    lab = d["gold_label"]

    # ignore -1 labels
    if lab == -1:
        next

    # define current meta data split
    meta_split = mag2bin(d["metadata"]["mag"])
    if user not in usr.keys():
        usr[user] = {}

    # current user
    current_user = usr[user]

    # define what to capture
    if meta_split not in current_user.keys():
        current_user[meta_split] = {"n": 0, "pos": 0, "tp": 0,
                                    "fp": 0, "fn": 0, "tn": 0}

    # update counts
    current_user[meta_split]["n"] = current_user[meta_split]["n"] + 1
    if lab == 1:
        current_user[meta_split]["pos"] = current_user[meta_split]["pos"] + 1

    if lab == ann == 1:
        current_user[meta_split]["tp"] = current_user[meta_split]["tp"] + 1

    if (lab == 0) & (ann == 1):
        current_user[meta_split]["fp"] = current_user[meta_split]["fp"] + 1

    if (lab == 1) & (ann == 0):
        current_user[meta_split]["fn"] = current_user[meta_split]["fn"] + 1

    if (lab == 0) & (ann == 0):
        current_user[meta_split]["tn"] = current_user[meta_split]["tn"] + 1

# calc summary stats for each user



#usr['HTMAMR38']
#
#q = Query()
#q.match("user_name",'HTMAMR38')
#tt = db.classifications.aggregate(q.build())
#for t in tt:
#    print(t)