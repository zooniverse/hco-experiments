################################################################

from swap.plots import traces, distributions, performance

from swap.plots.distributions import plot_pdf
from swap.plots.distributions import plot_class_histogram

from swap.plots.performance import plot_user_cm
from swap.plots.performance import plot_confusion_matrix
# from swap.plots.performance import plot_histogram
from swap.plots.performance import plot_roc

# 'using' imports to silence pep warnings
assert traces
assert distributions
assert performance

assert plot_pdf

assert plot_user_cm
assert plot_confusion_matrix
assert plot_class_histogram
assert plot_roc
