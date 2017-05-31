################################################################

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import statistics as st

from sklearn.neighbors.kde import KernelDensity
from scipy.signal import argrelextrema

import seaborn as sns


def _plot(func):
    def wrapper(fname, *args, **kwargs):
        func(*args, **kwargs)
        if fname:
            plt.savefig(fname, dpi=300)
        else:
            plt.show()
    return wrapper


def plot_kde(data):
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


@_plot
def plot_seaborn_density_split(scores, cutoff=1):
    scores = [item for item in scores if item[1] < cutoff]
    b0 = [item[1] for item in scores if item[0] == 0]
    b1 = [item[1] for item in scores if item[0] == 1]

    sns.distplot(np.array(b0), kde_kws={'label': 'Real 0'})
    sns.distplot(np.array(b1), kde_kws={'label': 'Real 1'})

    plt.ylabel('Number of subjects')
    plt.xlabel('Probability')


@_plot
def plot_class_histogram(score_export):
    data = score_export.roc()
    sorted_data = score_export.sorted_scores
    scores = score_export.scores
    # b0 = [item[1] for item in roc if item[0] == 0]
    # b1 = [item[1] for item in roc if item[0] == 1]

    # class bins for drawing the histogram
    b0 = []
    b1 = []
    # bins for drawing the purity and completeness lines
    # bins = [[0, 0, 0] for i in range(25)]

    for gold, p in data:
        # bin_ = int(p * 100 / 4)
        # if bin_ == 25:
        #     bin_ -= 1

        # print(bin_, gold, p)

        if gold == 0:
            b0.append(p)
            # bins[bin_][1] += 1
            # bins[bin_][2] += 1
        elif gold == 1:
            b1.append(p)

            # bins[bin_][0] += 1
            # bins[bin_][1] += 1

    ax = plt.subplot(111)

    # Draw the histogram
    ax.hist([b0, b1], 25, histtype='bar',
            label=['bogus', 'real'], stacked=True)
    ax.legend()

    ax.set_yscale('linear')
    ax.set_ylim(top=5000)
    # bins = np.array(bins)
    # print(bins)

    # Draw the purity curve
    line_ax = ax.twinx()
    line_ax.set_ylabel('% purity/completeness')
    line_ax.axis([0, 1, 0, 1])

    line_x = []
    line_y = []
    count = 0
    golds = 0
    for i in reversed(sorted_data):
        score = scores[i]
        count += 1
        if score.gold == 1:
            golds += 1

        line_x.append(score.p)
        line_y.append(golds / count)

    line_ax.plot(line_x, line_y, color='red')

    # Draw the completeness curve
    line_x = []
    line_y = []
    count = 0
    golds = 0
    for i in sorted_data:
        score = scores[i]
        count += 1
        if score.gold == 1:
            golds += 1

        line_x.append(score.p)
        line_y.append(golds)

    line_y = [y / count for y in line_y]

    line_ax.plot(line_x, line_y, color='orange')

    line_ax.legend(['Purity', 'Completeness'], loc=2)
    # line_ax.axis([0, 1, 0, 1])

    # Draw the purity/completeness curve
    # line_x = []
    # line_y = []
    # for i, bin_ in enumerate(bins):
    #     line_x.append(i * .04 + .02)
    #     line_y.append(bin_[0] / bin_[1])

    # ax2 = ax.twinx()
    # ax2.plot(line_x, line_y, color='red')
    # ax2.axis([0, 1, 0, 1])

    ax.set_ylabel('frequency')
    plt.xlabel('probability')
    # plt.title('Multiclass Probability Distribution')


@_plot
def multivar_scatter(data, title):
    plt.subplot(111)
    x, y, z = zip(*data)
    norm = mpl.colors.Normalize(vmin=min(z), vmax=max(z))
    plt.scatter(x, y, c=z, norm=norm, cmap='viridis')

    plt.colorbar()
    plt.title(title)
    plt.xlabel('Consensus')
    plt.ylabel('Controversial')


def plot_pdf(score_export, fname, swap=None, cutoff=1):
    cut_data = np.array([p for g, p in score_export.roc() if p < cutoff])

    plots = ['density', 'kde']
    n = len(plots)

    for i, f in enumerate(plots):
        plt.subplot(n, 1, i + 1)
        if f == 'density':
            plot_seaborn_density(cut_data)
        elif f == 'split':
            plot_seaborn_density_split(swap, cutoff)
        elif f == 'kde':
            plot_kde(cut_data)

    plt.suptitle('Probability Density Function')
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)

    if fname:
        plt.savefig(fname, dpi=300)
    else:
        plt.show()
