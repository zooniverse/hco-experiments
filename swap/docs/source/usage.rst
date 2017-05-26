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

Detailed Usage
--------------

Using the ui script::
    run_swap [options] {roc,swap} [other_options]

Commands
~~~~~~~~
    swap
        Interact with a SWAP instance
    roc
        Generate receiver-operator curve from multiple SWAP export files

Options
~~~~~~~
.. program:: run_swap

.. option:: -h, --help

    Show help message and exit

.. option:: --dir DIR

    Direct all file output to a different directory
.. option:: --p0 VALUE

    Set temporary p0 in config
.. option:: --epsilon VALUE

    Set temporary epsilon in config
.. option:: --pow

    controversial and consensus aggregation method
.. option:: --multiply

    controversial and consensus aggregation method

SWAP
~~~~

SWAP Syntax
```````````

Running swap commands::
    run_swap [options] swap [swap_options]

SWAP Options
````````````

.. program:: run_swap swap

.. option:: -h, --help

    Show help message and exit

.. option:: --save FILE

    Save SWAP to file

.. option:: --save-scores FILE

    Save SWAP scores export to file

.. option:: --load FILE

    Load a SWAP object from file

SWAP Plotting Options
`````````````````````
    
.. option:: --subject FILE

    Generate plot of subject tracks and output to file

.. option:: --utraces FILE

    Generate user track plots and output to file

.. option:: --user FILE

    Generate user confusion matrices and outname to file

.. option:: --hist FILE

    Generate multiclass histogram plot

.. option:: --dist DIST DIST

    Show distribution plot

.. option:: --diff [DIFF [DIFF ...]]

    Visualize performance difference between swap outputs

.. option:: --log FILE

    Write the entire SWAP export to file

.. note::
    Passing .. option:: - as a filename to the plotting functions will shows the plot
    with the builtin matplotlib viewer instead

Run Options
```````````

.. option:: --run

    Run the SWAP algorithm

.. option:: --train N

    Run swap with a test/train split. Restricts sample
    size of gold labels to 'n'

.. option:: --controversial N

    Run swap with a test/train split, using the
    most/least controversial subjects

.. option:: --consensus N

    Run swap with a test/train split, using the
    most/least consensus subjects

.. option:: --stats

    Display run statistics

.. option:: --shell

    Drop to a python shell after executing other commands

ROC
~~~

ROC Syntax
``````````
Running roc commands::
    ``run_swap [options] roc [roc_options]``

ROC Options
```````````
    .. option:: -h, --help

        Show help message and exit
    
    .. option:: -a, --add LABEL FILE

        Add a swap run to the plot.

        Label:
            Label to use in the plot
        File:
            File to load from. Should be a pickled score export
    .. option:: -o, --output FILE

        Save the plot to file. If .. option:: - is passed, shows the plot
        with the builtin matplotlib viewer instead