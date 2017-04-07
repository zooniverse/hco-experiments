# import moudules
from swap.control import Control
from swap.mongo import DB
from swap.config import Config
from swap.mongo import Query
import pandas as pd

# Run SWAP
control = Control(0.1, 0.5)
control.process()

# get User data
users = control.getSWAP().exportUserData()

# get raw classifications
db = DB()
cfg = Config()
classifications = db.classifications

# Define a query
q = Query()
fields = ['user_name', 'subject_id', 'annotation', 'gold_label']

cls = classifications.aggregate(q.build())

# prepare data frame with user, cl_id, type
res = list()
for cl in cls:
    rec = [cl['user_name'], cl['gold_label'], cl['annotation'],
           cl['machine_score'], cl['object_id']]
    res.append(rec)


# convert to data frame
df = pd.DataFrame(res,columns=('user_name','gold_label','annotation',
                               'machine_score','object_id'))

# export for analysis in R
df.to_csv('D:\Studium_GD\Zooniverse\Data\export\classifications_dat.csv')


users['HTMAMR38']

labs = getLabelReal(subs)
ev =  eval_classifications(y_true=labs['actual'],
                           y_pred=labs['prob'],
                           pos_label=1,
                           excl_label=-1)