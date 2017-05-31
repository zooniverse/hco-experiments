README
======

Documentation
-------------

Find full documentation and more at [ReadTheDocs](http://hco-experiments.readthedocs.io/en/latest/)

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

Machine Learning
----------------

### Get the data
[Pan-STARRS1 Medium Deep training set](https://www.dropbox.com/s/dft3qpnfn3clv9y/md_20x20_skew4_SignPreserveNorm_with_confirmed1.mat?dl=0) - [Wright et al. 2015](https://arxiv.org/abs/1501.05470)

[Pan-STARRS1 3pi training set](https://www.dropbox.com/s/btzji6ug9ikwlwm/3pi_20x20_skew2_signPreserveNorm.mat?dl=0) - used to train Supernova Hunters classifier

[STL-10 dataset](https://cs.stanford.edu/~acoates/stl10/) - [Coates et al. 2011](http://cs.stanford.edu/~acoates/papers/coatesleeng_aistats_2011.pdf)

[STL-10 grayscale mean-subtracted patches](https://www.dropbox.com/s/gairqidpyjxtzah/patches_stl-10_unlabeled_meansub_20150409_psdb_6x6.mat?dl=0) - patches used to train sparse filter
