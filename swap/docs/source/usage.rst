.. usage:
UI Usage
========

There are a lots of different operations that may be desirable with SWAP.
This is a tool to run various scripts from the command line in a consistent manner.

Useful Examples
---------------

Running Swap
    ``run_swap swap --run``

Running Swap with custom p0 variable
    ``run_swap --p0 0.01 swap --run``

Running Swap then saving it
    ``run_swap swap --run --save swap.pkl``

Loading pickled Swap and exporting scores
    ``run_swap swap --load swap.pkl --save-score scores.pkl``

Loading pickled Swap and export confusion matrix plot
    ``run_swap swap --load swap.pkl --user user.png``

Generate a ROC curve from pickled score exports
    ``run_swap roc -a label1 score_export1.pkl -a label2 score_export2.pkl --output roc.png``

.. note::
    Most of these examples assume you've added properly installed the SWAP
    package using distutils, such that run_swap exists in your PATH variable
    and points to the __main__.py script.
    You can install the SWAP package by running::
        python setup.py install
    from the project root. Make sure you have a virtual environment setup which
    points to a python version >=3.4

Launching Caesar
----------------

Some examples to launch caesar


Interacting with SWAP
=====================

After running SWAP, you probably want to analyze the data. SWAP provides a couple
convenience classes to collect and export the data.

To get the score history of each subject, SWAP can export a HistoryExport object.

.. highlight:: python

::

    history = swap.history_export()
    for id_, gold, scores in history:
        # do something

For a more lightweight score export (which only includes the final score), you
can export a ScoreExport object.

.. highlight:: python

::

    scores = swap.score_export()
    for id_, gold, score in scores.full():
        # do something


Detailed Usage
==============

.. argparse::
    :ref: swap.ui._get_parser
    :prog: run_swap
