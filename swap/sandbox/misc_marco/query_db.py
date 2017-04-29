# Some functions / statements to query the database

# load modules
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


# classification ids
q = Query()
fields = ['classification_id']
q.project(fields)
tt = db.classifications.aggregate(q.build())
for i in range(0,10):
    c = tt.next()
    print(c)

# query specific user
q.match("user_name",'022henry')
tt = db.classifications.aggregate(q.build())
for t in tt:
    print(t)


# export classifications to disk
q = Query()
fields = ['classification_id',"subject_id", "metadata","gold_label",
          "machine_score","annotation","user_name"]
q.project(fields)
cl = db.classifications.aggregate(q.build())

res = dict()
for c in cl:
    # c = cl.next()
    c['mag'] = c['metadata']['mag']
    c['seeing'] = c['metadata']['seeing']
    c.pop('metadata', None)
    c.pop('_id', None)
    res[c['classification_id']] = c


# create pandas data frame from dictionary
psubs = pd.DataFrame.from_dict(res,orient="index")

# export for analysis in R
psubs.to_csv('D:\Studium_GD\Zooniverse\Data\export\classification_data.csv',
             index=False, index_label=False)
