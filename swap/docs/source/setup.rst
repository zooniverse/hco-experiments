
Getting Started
===============

Installation
------------

Recommended to set up a virtual environment and install SWAP
and its dependencies inside. For more information, consult the docs for
`virtual environments <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_ and `conda <https://conda.io/docs/using/>`_. 

To install SWAP, first clone the git repository. Then navigate
to the project directory and install with::

    pip install hco-experiments/swap

Pip can also install SWAP in development mode. This means pip will install
the project in editable mode. To do this, navigate to the project
directory and run::

    pip install -e hco-experiments/swap[dev,test]

After installing, the general command to invoke the SWAP ui
is `run_swap`. To run SWAP and pickle and save, run::
    
    run_swap swap --run --save output.pkl

More detailed usage examples are available at :doc:`usage`.]
