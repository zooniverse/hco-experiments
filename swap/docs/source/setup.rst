
Getting Started
===============

Installation
------------

Recommended to set up a virtual environment and install SWAP
and its dependencies inside. For more information, consult the docs for
`virtual environments <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_ and `conda <https://conda.io/docs/using/>`_. 

To install SWAP, you can use pip to install directly from the repository::

    pip install "git+git://github.com/miclaraia/hco-experiments#egg=SWAP&subdirectory=swap"

*Development Mode:* Pip can also install SWAP in development mode. This means pip will install
the project in editable mode, so changes to the source affect the runtime version.
It will also install additional dependencies for testing and development.
To do this, clone the git repository, navigate to the projectd directory, and run::

    pip install -e hco-experiments/swap[dev,test]

After installing, the general command to invoke the SWAP ui
is `run_swap`. To run SWAP and pickle and save, run::
    
    run_swap swap --run --save output.pkl

More detailed usage examples are available at :doc:`usage`.
