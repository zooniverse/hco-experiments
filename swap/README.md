README
======


Getting Started
---------------

Recommended to set up a virtual environment and install SWAP
and its dependencies inside. You can find more information about virtual environments
[here](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/).

### Installing SWAP

To install SWAP regularly, run

    pip install {PATH_TO_SWAP}

To install SWAP in development mode, run::

    pip install -e {PATH_TO_SWAP}[dev,test]

Using SWAP
----------

After installing, there are a number of commands available for running SWAP.
These include tools to create plots and export SWAP scores to file.

Basic syntax is

    run_swap [options] COMMAND [options]

Command can be one of `{roc, swap}`

To run swap and pickle and save, run

    run_swap swap --run 

Find more details by running

    run_swap -h

or, for more details about SWAP specific commands, run

    run_swap swap -h