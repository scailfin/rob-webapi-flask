.. figure:: https://github.com/scailfin/rob-webapi-flask/blob/flowserv/docs/graphics/header-webapi.png
   :align: center
   :alt: ROB Web Service Implementation (using Flask)


About
=====

This is the default RESTful Web API implementation for the `Reproducible Open Benchmarks for Data Analysis Platform (ROB) <https://github.com/scailfin/flowserv-core>`_ using  the `Flask web framework <https://flask.palletsprojects.com>`_.



Installation and Configuration
==============================

The following installation instructions assume that you install all packages in a local folder `~/projects/rob`.

.. code-block:: bash

    # -- Change the working directory

    cd ~/projects/rob


The Reproducible Open Benchmarks platform is implemented in Python. We recommend using a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for the installation.

.. code-block:: bash

    # -- Create a new virtual environment
    virtualenv venv
    # -- Activate the virtual environment
    source venv/bin/activate


The Flask Web API for ROB requires the ``flowserv`` package. The following steps will install all packages from the respective GitHub repositories:


.. code-block:: bash

    git clone git@github.com:scailfin/flowserv-core.git
    pip install -e flowserv-core
    git clone git@github.com:scailfin/rob-webapi-flask.git
    pip install -e rob-webapi-flask


The primary configuration parameters are defined in the `ROB Configuration documentation <https://github.com/scailfin/flowserv-core/blob/master/docs/configuration.rst>`_. Two additional environment variables are defined by the Web API:

- **ROB_WEBAPI_LOG**: Directory path for API logs (default: ``$FLOWSERV_API_DIR/log``)
- **ROB_WEBAPI_CONTENTLENGTH**: Maximum size of uploaded files (default: ``16MB``)

If you run the Flask application from the command line in developer mode using ``flask run``, you also need to set the following environment variables:

.. code-block:: bash

    export FLASK_APP=robflask.api
    export FLASK_ENV=development


There are also more detailed instructions on the `Demo Setup site <https://github.com/scailfin/rob-webapi-flask/blob/master/docs/demo-setup.rst>`_ to setup and run the Web API.



Command Line Interface
======================

The ``robflask`` package includes a command line tool to setup the ROB database and for creating and manipulating benchmarks.

Initialize the ROB database
---------------------------

Initialize database and base directories for the Reproducible Open Benchmarks (ROB) Web API. The configuration parameters for the database are taken from the respective environment variables. Creates the API base directory if it does not exist.

.. code-block:: console

    Usage: robadm init [OPTIONS]

    Options:
      -d, --dir FILE  Base directory for API files (overrides FLOWSERV_API_DIR).
      --help          Show this message and exit.

Create and delete Benchmarks
----------------------------

Create a new benchmark.

.. code-block:: console

    Usage: robadm benchmarks create [OPTIONS]

    Options:
      -n, --name TEXT          Unique benchmark name.  [required]
      -d, --description TEXT   Short benchmark description.
      -i, --instructions FILE  File containing instructions for participants.
      -s, --src DIRECTORY      Benchmark template directory.
      -u, --url TEXT           Benchmark template Git repository URL.
      -f, --specfile FILE      Optional path to benchmark specification file.
      --help                   Show this message and exit.


Delete a given benchmark.

.. code-block:: console

    Usage: robadm benchmarks delete [OPTIONS] IDENTIFIER

    Options:
      --help  Show this message and exit.
