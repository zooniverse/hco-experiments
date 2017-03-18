# Check Seeing Data
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
cl = classifications.find()
for c in cl:
    time.sleep(3)
    print(c)


# Retrieve data per Subject
g = Group()
g.id(["subject_id", "metadata","gold_label","machine_score"])
g.build()
sub = db.classifications.aggregate([g.build()], allowDiskUse=True,
                                   batchSize=int(1e5))

# run SWAP without meta data split
control = Control(0.01, 0.5)
control.process()
swap_sub = control.getSWAP().exportSubjectData()


# create dictionary with all subjects
subs = dict()
for s in sub:
    # check if subject is in SWAP (no -1 gold labels)
    if s['_id']['subject_id'] in swap_sub:
        lab = swap_sub[s['_id']['subject_id']]['label']
        score = swap_sub[s['_id']['subject_id']]['score']
    else:
        lab = None
        score = None

    # create dictionary
    sub_dic = {'gold_label':  s['_id']['gold_label'],
               'machine_score': s['_id']['machine_score'],
               'label': lab,
               'score': score}
    # add meta data
    for k,v in s['_id']['metadata'].items():
        sub_dic[k] = v

    # add dictionary to current subject
    subs[s['_id']['subject_id']] = sub_dic


# create pandas data frame from dictionary
psubs = pd.DataFrame.from_dict(subs,orient="index")

# export for analysis in R
psubs.to_csv('D:\Studium_GD\Zooniverse\Data\export\subject_dat.csv')


# convert to magnitude bin
def mag2bin(val):
    if np.isnan(val):
        return val
    mag_ranges = [(13, 18), (18, 19), (19, 20), (20, 23)]
    bin_val = min([x[1] for x in mag_ranges if val<=x[1]])
    return bin_val

psubs['mag_bin'] = psubs.apply(lambda row: mag2bin(row['mag']),axis=1)


# visualize data
import seaborn as sns
sns.set()
sns.jointplot(x="machine_score", y="mag", data=psubs)
sns.jointplot(x="seeing", y="mag", data=psubs)
sns.jointplot(x="seeing", y="mag", data=psubs[(psubs['gold_label'] == 1)])
sns.jointplot(x="seeing", y="mag", data=psubs[(psubs['gold_label'] == 0)])
sns.pairplot(psubs,vars=['seeing'],hue='mag_bin')

