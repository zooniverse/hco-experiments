UI
**

There are a lots of different operations that may be desirable with SWAP.
This is a tool to run various scripts from the command line in a consistent manner.

Useful Examples
###############

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
    Most of these examples assume you've added the main.py file in the
    project root to your path. This can be done on linux with::
        ln -s {SWAP root folder}/main.py {home directory}/.local/bin/run_swap
    and ensuring that `$HOME/.local/bin` is in your PATH variable

Detailed Usage
##############

run_swap
========

Syntax
------
    ``run_swap [options] {roc,swap} [other_options]``

Commands
--------
    swap
        Interact with a SWAP instance
    roc
        Generate receiver-operator curve from multiple SWAP export files

Options
-------
    ``-h, --help``
        Show help message and exit
    ``--dir DIR``
        Direct all file output to a different directory
    ``--p0 VALUE``
        Set temporary p0 in config
    ``--epsilon VALUE``
        Set temporary epsilon in config
    ``--pow``
        controversial and consensus aggregation method
    ``--multiply``
        controversial and consensus aggregation method

SWAP
====

Syntax
------
    ``run_swap [options] swap [swap_options]``

Options
-------
    ``-h, --help``
        Show help message and exit
    
    ``--save FILE``
        Save SWAP to file
    
    ``--save-scores FILE``
        Save SWAP scores export to file
    
    ``--load FILE``
        Load a SWAP object from file

Plotting Options
^^^^^^^^^^^^^^^^
    
    ``--subject FILE``
        Generate plot of subject tracks and output to file
    
    ``--utraces FILE``
        Generate user track plots and output to file
    
    ``--user FILE``
        Generate user confusion matrices and outname to file
    
    ``--hist FILE``
        Generate multiclass histogram plot
    
    ``--dist DIST DIST``
        Show distribution plot
    
    ``--diff [DIFF [DIFF ...]]``
        Visualize performance difference between swap outputs
    
    ``--log FILE``
        Write the entire SWAP export to file
    
    .. note::
        Passing ``-`` as a filename to the plotting functions will shows the plot
        with the builtin matplotlib viewer instead

Run Options
^^^^^^^^^^^
    ``--run``
        Run the SWAP algorithm

    ``--train N``
        Run swap with a test/train split. Restricts sample
        size of gold labels to 'n'
    
    ``--controversial N``
        Run swap with a test/train split, using the
        most/least controversial subjects
    
    ``--consensus N``
        Run swap with a test/train split, using the
        most/least consensus subjects
    
    ``--stats``
        Display run statistics
    
    ``--shell``
        Drop to a python shell after executing other commands

ROC
===

Syntax
------
    ``run_swap [options] roc [roc_options]``

Options
-------
    ``-h, --help``
        Show help message and exit
    
    ``-a, --add LABEL FILE``
        Add a swap run to the plot.

        Label:
            Label to use in the plot
        File:
            File to load from. Should be a pickled score export
    ``-o, --output FILE``
        Save the plot to file. If ``-`` is passed, shows the plot
        with the builtin matplotlib viewer instead

Autodoc
#######
Module
======
.. automodule:: swap.ui

UI
==
.. autoclass:: swap.ui.UI
    :show-inheritance:
    :members:
    :private-members:

Interface
=========
.. autoclass:: swap.ui.Interface
    :show-inheritance:
    :members:
    :private-members:
