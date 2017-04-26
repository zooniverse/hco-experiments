################################################################

import numpy as np
import matplotlib.pyplot as plt
import statistics as st

from sklearn.neighbors.kde import KernelDensity
from scipy.signal import argrelextrema

import seaborn as sns


def plot_kernel_density(data):
    bw = 1.06 * st.stdev(data) / (len(data) ** .2)
    kde = KernelDensity(kernel='gaussian', bandwidth=bw).fit(
        np.array(data).reshape(-1, 1))
    s = np.linspace(0, 1)
    e = kde.score_samples(s.reshape(-1, 1))
    plt.plot(s, e)

    mi, ma = argrelextrema(e, np.less)[0], argrelextrema(e, np.greater)[0]
    print("Minima: %s" % s[mi])
    print("Maxima: %s" % s[ma])

    plt.plot(s[:mi[0] + 1], e[:mi[0] + 1], 'r',
             s[mi[0]:mi[1] + 1], e[mi[0]:mi[1] + 1], 'g',
             s[mi[1]:], e[mi[1]:], 'b',
             s[ma], e[ma], 'go',
             s[mi], e[mi], 'ro')

    plt.xlabel('Probability')


def plot_jenks_breaks(data):
    import jenkspy
    breaks = jenkspy.jenks_breaks(np.array(data).reshape(-1, 1), nb_class=3)
    print(breaks)
    for x in breaks:
        plt.plot([x], [5], 'o')


def plot_seaborn_density(data):
    sns.distplot(data)
    plt.ylabel('Number of subjects')
    plt.xlabel('Probability')


def plot_seaborn_density_split(swap, cutoff=1):
    roc = swap.roc_export()
    roc = [item for item in roc if item[1] < cutoff]
    b0 = [item[1] for item in roc if item[0] == 0]
    b1 = [item[1] for item in roc if item[0] == 1]

    sns.distplot(np.array(b0), kde_kws={'label': 'Real 0'})
    sns.distplot(np.array(b1), kde_kws={'label': 'Real 1'})

    plt.ylabel('Number of subjects')
    plt.xlabel('Probability')


def plot_probability_density(data, fname, swap=None, cutoff=1):
    cut_data = np.array([x for x in data if x < cutoff])

    plots = ['density', 'kde']
    n = len(plots)

    for i, f in enumerate(plots):
        plt.subplot(n, 1, i + 1)
        if f == 'density':
            plot_seaborn_density(cut_data)
        elif f == 'split':
            plot_seaborn_density_split(swap, cutoff)
        elif f == 'kde':
            plot_kernel_density(data)

    plt.suptitle('Probability Density Function')
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)

    if fname:
        plt.savefig(fname, dpi=300)
    else:
        plt.show()
