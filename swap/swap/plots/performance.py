################################################################

import matplotlib.pyplot as plt
import numpy as np
import math

from sklearn.metrics import roc_curve
from sklearn.metrics import auc

import logging
logger = logging.getLogger(__name__)


def plot_user_cm(swap, fname):
    data = []
    for user in swap.users:
        score = user.score
        n = len(user.ledger)

        data.append((*score, n))

    plot_confusion_matrix(data, "User Confusion Matrices", fname)


def plot_histogram(data, title, fname, dpi=300):
    """
        Generate a histogram plot
    """
    # the histogram of the data
    n, bins, patches = plt.hist(
        data, 50, normed=1,
        facecolor='green', alpha=0.75)

    # add a 'best fit' line
    # y = mlab.normpdf( bins, mu, sigma)
    # l = plt.plot(bins, y, 'r--', linewidth=1)

    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    plt.axis([0, 1, 0, 10])
    plt.grid(True)

    plt.show()


def plot_roc(title, iterator, fname=None, dpi=300):
    plt.figure(1)

    for label, data in iterator:
        y_true = []
        y_score = []

        for t in data:
            y_true.append(t[0])
            y_score.append(t[1])

        y_true = np.array(y_true)
        y_score = np.array(y_score)

        # Compute fpr, tpr, thresholds and roc auc
        fpr, tpr, thresholds = roc_curve(y_true, y_score)
        roc_auc = auc(fpr, tpr, True)
        # roc_auc = 0

        # Plot ROC curve
        plt.plot(fpr, tpr, label='%s (area = %0.3f)' % (label, roc_auc))

    plt.plot([0, 1], [0, 1], 'k--')  # random predictions curve
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel('False Positive Rate or (1 - Specifity)')
    plt.ylabel('True Positive Rate or (Sensitivity)')
    plt.title('Receiver Operating Characteristic for %s' % title)
    plt.legend(loc="lower right")

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()


def plot_confusion_matrix(data, title, fname, dpi=300):
    # """ Plot User Skill """
    # # Loop over all users
    # user_data = swappy.exportUserData()
    # # all users
    # unique_users = user_data.keys()
    # # max classifications
    # max_class = 0
    # # number of user processed
    # counter = 0
    # for user in unique_users:
    #     n_class_user = len(user_data[user]['gold_labels'])
    #     max_class = max(max_class, n_class_user)
    #     plt.plot(user_data[user]['score_1_history'][-1],
    #              user_data[user]['score_0_history'][-1], "o",
    #              ms=(n_class_user)/500,
    #              color="#3F88C5", alpha=0.5)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for item in data:
        ax.plot(item[1], item[0],
                 'o', ms=item[2] / 500,
                 color="#3F88C5", alpha=0.5)

    # Quadrant labels
    ax.text(0.03, 0.03, "Obtuse")
    ax.text(0.75, 0.03, "Optimistic")
    ax.text(0.03, 0.95, "Pessimistic")
    ax.text(0.8, 0.95, "Astute")

    # Quadrant divider lines
    ax.plot([0.5, 0.5], [0, 1], "k--", lw=1)
    ax.plot([0, 1], [0.5, 0.5], "k--", lw=1)
    ax.plot([0, 1], [1, 0], "k-", lw=1)

    # Axis labels
    plt.xlabel("P(\'real\'|real)")
    plt.ylabel("P(\'bogus\'|bogus)")
    plt.axes().set_aspect('equal')

    # Plot Title
    plt.title(title)

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()


def plot_matrix_difference(data, title, fname):
    for x, y, n in data:
        if n < 0:
            color = '#C10505'
            n = -n
        elif n == 0:
            color = '#3F88C5'
        else:
            color = '#000000'

        plt.plot(x, y, 'o', ms=5, color=color, alpha=.5)

    # Quadrant divider lines
    plt.plot([0, 0], [-1, 1], "k--", lw=1)
    plt.plot([-1, 1], [0, 0], "k--", lw=1)
    # plt.plot([0, 1], [1, 0], "k-", lw=1)

    # Plot Title
    plt.title(title)

    if fname:
        plt.savefig(fname, dpi=300)
    else:
        plt.show()


def p_diff(base_score, other, fname, y_axis=None,
           aspect=None, x_axis=None):

    # Configure subplots in 'n x n' square grid
    count = len(other)
    w = math.ceil(math.sqrt(count))
    h = math.ceil(count / w)

    # fig = plt.figure()

    for i, item in enumerate(other):
        label, other_score = item

        # Select the right subplot position
        # if aspect is not None:
        #     ax = fig.add_subplot(
        #         w, h, i + 1, adjustable='box',
        #         aspect=9 / 16)
        # else:
        #     ax = plt
        plt.subplot(w, h, i + 1)

        data = []
        a_dict = base_score.dict()
        b_dict = other_score.dict()

        for id_ in a_dict:
            if id_ in b_dict:
                a = a_dict[id_].p
                b = b_dict[id_].p
                data.append((a, b))

        scatter_plot(data)

        # Plot Title
        plt.title(label)

        if y_axis is not None:
            plt.ylabel(y_axis)

        if x_axis is not None:
            plt.xlabel(x_axis)

        print(label)

    plt.tight_layout()
    plt.subplots_adjust(top=0.93)

    if fname:
        plt.savefig(fname, dpi=300)
    else:
        plt.show()


def scatter_plot(data):
    x = [i[0] for i in data]
    y = [i[1] for i in data]
    plt.plot(x, y, 'o', alpha=.5, ms=1)
