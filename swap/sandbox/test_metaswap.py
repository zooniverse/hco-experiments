# Test meta data splits
from swap.control import MetaDataControl
from swap.mongo import Query
import matplotlib.pyplot as plt


def plot_swap_users(swappy, title, name):
    """ Plot User Skill """
    # Loop over all users
    user_data = swappy.exportUserData()
    # all users
    unique_users = user_data.keys()
    # max classifications
    max_class = 0
    # number of user processed
    counter = 0
    for user in unique_users:
        n_class_user = len(user_data[user]['gold_labels'])
        max_class = max(max_class, n_class_user)
        plt.plot(user_data[user]['score_1_history'][-1],
                 user_data[user]['score_0_history'][-1], "o",
                 ms=(n_class_user)/500,
                 color="#3F88C5", alpha=0.5)
        counter += 1

    plt.text(0.03, 0.03, "Obtuse")
    plt.text(0.75, 0.03, "Optimistic")
    plt.text(0.03, 0.95, "Pessimistic")
    plt.text(0.8, 0.95, "Astute")
    plt.plot([0.5, 0.5], [0, 1], "k--", lw=1)
    plt.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    plt.plot([0, 1], [1, 0], "k-", lw=1)
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')
    plt.title(title)
    plt.savefig(name)
    plt.show()


def plot_swap_subjects(swappy, title, name):
    """ Plot subject tracks """
    subject_data = swappy.exportSubjectData()
    colourmap = ["#669D31", "#F00200"]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    count = 0
    for subject_id in subject_data.keys():
        if count == 1000:
            break
        #print(count)
        colour = colourmap[subject_data[subject_id]['gold_label']]
        history = subject_data[subject_id]['history']
        #print(history)
        ax.plot([0.01]+history, range(len(history)+1), "-",
                color=colour, lw=1, alpha=0.1)
        """
        if subjectData[subject_id]["gold_label"] == "1":
            ax.plot([0.01]+history,range(len(history)+1),"-",color=colour,lw=1, alpha=0.5,zorder=1000)
        else:
            ax.plot([0.01]+history,range(len(history)+1),"-",color=colour,lw=1, alpha=0.5)
        """
        count += 1
    plt.xlim(-0.01, 1.01)
    ax.set_yscale("log")
    plt.gca().invert_yaxis()
    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.title(title)
    plt.savefig(name)
    plt.show()

# Extract labels
def getLabelReal(subs):
    res = {'actual': [], 'predicted': [], 'prob': []}
    for sub in subs.values():
        res['actual'].append(sub['gold_label'])
        res['predicted'].append(sub['label'])
        res['prob'].append(sub['score'])
    return res

# From scikit-learn website
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """

    import numpy as np
    import itertools

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, round(cm[i, j],2),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def plot_swap_subject_cm(swappy,title,name):

    from sklearn.metrics import confusion_matrix
    import numpy as np


    subs = swappy.exportSubjectData()
    labs = getLabelReal(subs)

    # Compute confusion matrix
    cnf_matrix = confusion_matrix(labs['actual'], labs['predicted'])
    np.set_printoptions(precision=2)
    plt.figure()
    plot_confusion_matrix(cnf_matrix, classes=['Bogus','Real'],
                          normalize=False,
                          title=title)

    plt.savefig(name)
    plt.show()


    #import pandas as pd
    #ps = pd.Series([(labs['actual'][x],labs['predicted'][x]) for x in range(0, len(labs['actual']))])
    #counts = ps.value_counts()
    #counts



def eval_classifications(y_true, y_pred, pos_label, excl_label=None):
    """ Evaluate Classifications

    Parameters:
    -----------
        y_true: list
            true labels
        y_pred: list
            predicted probabilities of bein of pos label (0:1)
        pos_label: int/str
            positive lavel occurring in y_true

    Output:
    -------
        res: dict
            various evaluation metrics
    """
    # load modules
    from sklearn.metrics import roc_curve, auc, confusion_matrix

    # exclude labels
    if excl_label is not None:
        ii = [i for i in range(0,len(y_true)) if y_true[i] != excl_label]
        y_true = [y_true[i] for i in ii]
        y_pred = [y_pred[i] for i in ii]

    # calculate ROC values for a range of thresholds
    # to plot ROC curves
    fpr, tpr, thresholds = roc_curve(y_true,
                                     y_pred,
                                     pos_label=pos_label)
    # AUC value
    roc_auc = auc(fpr, tpr)

    # FoM - FNR at 1% FPR
    # Figure of Merit: according to Darryls paper
    i_fpr1 = max([i for i in range(0, len(fpr)) if fpr[i] <= 0.01])
    fnr1 = 1-tpr[i_fpr1]
    # probability at optimal FoM score
    fom_score = thresholds[i_fpr1]

    # confusion matrix at optimal FoM
    if pos_label is not None:
        y_true_opt = [1 if l == pos_label else 0 for l in y_true]
        y_pred_opt = [1 if x >= fom_score else 0 for x in y_pred]

    cfm = confusion_matrix(y_true_opt, y_pred_opt)
    # return results
    res = {'auc': roc_auc,
           'fom_score': fom_score,
           'fom_fnr': fnr1,
           'cfm': cfm,
           'roc': {'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds}}
    return res

subs = controls[0].getSWAP().exportSubjectData()
labs = getLabelReal(subs)
y_true = labs['actual']



if __name__ == '__main__':

    # postfix for plots
    pfx = '_Rev'

    # function to process one magnitude range
    def processMagRange(lower,upper):
        control = MetaDataControl(0.01, 0.5, 'mag', lower, upper)
        control.process()
        plot_swap_subjects(control.getSWAP(),
                           title="Subject Tracks - %d-%d Mag" %
                                 (lower, upper),
                           name="subject_tracks_%d_%d%s.pdf" %
                                (lower, upper, pfx))
        plot_swap_users(control.getSWAP(),
                        title="User Profiles - %d-%d Mag" % (lower,upper),
                        name="User_profiles_%d_%d%s.pdf" % (lower,upper,pfx))
        plot_swap_subject_cm(control.getSWAP(),
                             title="Subject CM - %d-%d Mag" % (lower,upper),
                             name="Subject_CM_%d_%d%s.pdf" % (lower,upper,pfx))
        subs = control.getSWAP().exportSubjectData()
        labs = getLabelReal(subs)
        ev =  eval_classifications(y_true=labs['actual'],
                                   y_pred=labs['prob'],
                                   pos_label=1,
                                   excl_label=-1)
        return control, ev

    # Processs different magnitude ranges
    mag_ranges = [(13,18), (18,19), (19,20), (20,23)]
    res = [processMagRange(x[0],x[1]) for x in mag_ranges]
    controls = [x[0] for x in res]
    evals = [x[1] for x in res]


    # define some nice colors
    import brewer2mpl
    bmap = brewer2mpl.get_map("Set1","Qualitative",len(evals))
    colors = bmap.mpl_colors

    # plot over all roc curves
    lw = 1
    for i in range(0,len(evals)):
        # plot specific magnitude range
        plt.plot(evals[i]['roc']['fpr'], evals[i]['roc']['tpr'], lw=2,
                 color=colors[i],
                 label='Mag: %d-%d (auc = %0.2f)' % (mag_ranges[i][0],
                                   mag_ranges[i][1],evals[i]['auc']))

    # finalize roc curves plot
    plt.plot([0, 1], [0, 1], linestyle='--', lw=lw, color='k',
         label='Random')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC - Magnitude Ranges')
    plt.legend(loc="lower right")
    plt.savefig("ROC_comparison_magnitudes%s.pdf" % (pfx))
    plt.show()


    # plot over all confusion matrices
    plt.figure(1)
    for i in range(0,len(evals)):
        # plot specific magnitude range
        plot_range = 221 + i
        plt.subplot(plot_range)
        plot_confusion_matrix(evals[i]['cfm'],classes=['Real','Bogus'],
                              title='Mag: %d-%d' %
                              (mag_ranges[i][0],mag_ranges[i][1]),
                              normalize=True)

    plt.savefig("CM_comparison_optimal_FoM%s.pdf" % (pfx))
    plt.show()

    # Inspect extreme subjects with 1.0 or 0.0 score
    for i in range(0,len(controls)):
        sub = controls[i].getSWAP().exportSubjectData()
        sub_ext = {k:v for k,v in sub.items() if v['score'] == 1 or v['score'] ==0}
        # proportion of extreme values (0.0 or 1.0)
        prop = len(sub_ext.keys()) / len(sub.keys())
        print("--------------------------------------")
        print("Magnitude range: %d-%d " % (mag_ranges[i][0],mag_ranges[i][1]))
        print("Proportion Extreme/All: %s" % (prop))


#    usr = controls[0].getSWAP().exportUserData()
#    sub1 = {k:v for k,v in sub.items() if len(v['history']) > 1}
#    sub1 = {k:v for k,v in sub1.items() if v['history'][1] == 1}
#
#    sub1[4547164]
#
#
#    # select one subject
#    from swap.mongo import DB
#    from swap.config import Config
#    db = DB()
#    cfg = Config()
#    classifications = db.classifications
#    q = Query()
#    q.match(key="subject_id",value=4547164)
#    q.build()
#    classifications = classifications.aggregate(q.build())
#    cl = [cl for cl in classifications]
#    usr['leonie_van_vliet']
#    usr['WildWithin']
#    'Jose_Campos'
#    'MerylPG'





#def test_subject_gold_label_1():
#    swap = SWAP(p0=0.1, epsilon=0)
#
#    # define some users and their skills
#    swap.processOneClassification(Classification(1, 1, 0, 1))
#    swap.processOneClassification(Classification(2, 1, 0, 1))
#    swap.processOneClassification(Classification(3, 1, 0, 1))
#    swap.processOneClassification(Classification(4, 1, 0, 1))
#
#    export = swap.exportSubjectData()
#    pprint(export)
#    assert export[1]['gold_label'] == 1




