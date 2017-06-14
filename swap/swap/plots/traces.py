################################################################

import matplotlib.pyplot as plt


def plot_user(swap, fname):
    """
        Generate a trace plot of the average of each user's scores
        change with each classification

        Args:
            fname: Save the plot to file.
                   Shows the plot instead if None
    """
    export = swap.export()
    data = []
    for item in export['users'].values():
        h0 = item['score_0_history']
        h1 = item['score_1_history']

        h = []
        for i, v0 in enumerate(h0):
            if len(h1) <= i:
                v1 = h1[-1]
            else:
                v1 = h1[i]
            h.append((v0 + v1) / 2)
        data.append((1, h))

    plot_tracks(data, 'User Combined Tracks', fname, scale='log')


def plot_subjects(export, fname):
    """
        Generate a trace plot of how each subject's score changes
        with each classification
    """
    plot_tracks(export.traces(), 'Subject Tracks', fname)

    # export = swap.export()
    # print(fname)
    # data = [(d['gold_label'], d['history'])
    #         for d in export['subjects'].values()]
    # plot_tracks(data, 'Subject Tracks', fname)


def plot_tracks(data, title, fname, dpi=300, scale='log'):
    """
        Plot subject tracks

        Args:
            data: Should be a list of tuples of the form
                  (gold label, [subject history])
            title: Title of the plot
            fname: Save the plot to file.
                   Shows the plot instead if None
            dpi: Passed to matplotlib
            scale: ('log'|'linear')
    """
    cmap = ["#669D31", "#F00200", "#000000"]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    count = 0
    for gold, history in data:
        if count == 1000:
            break

        ax.plot(
            [0.01] + history,
            range(len(history) + 1),
            "-",
            color=cmap[gold],
            lw=1,
            alpha=0.1)

        count += 1

    plt.xlim(-0.01, 1.01)
    ax.set_yscale(scale)
    plt.gca().invert_yaxis()

    plt.xlabel("P(real)")
    plt.ylabel("number of classificaions")
    plt.title(title)

    if fname:
        plt.savefig(fname, dpi=dpi)
    else:
        plt.show()
