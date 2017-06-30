################################################################

try:
    from swap.plots import traces, distributions, performance

    from swap.plots.distributions import plot_pdf
    from swap.plots.distributions import plot_class_histogram

    from swap.plots.performance import plot_user_cm
    from swap.plots.performance import plot_confusion_matrix
    # from swap.plots.performance import plot_histogram
    from swap.plots.performance import plot_roc
except ImportError:
    traces = None
    distributions = None
    performance = None
    plot_pdf = None
    plot_class_histogram = None
    plot_user_cm = None
    plot_confusion_matrix = None
    plot_roc = None
