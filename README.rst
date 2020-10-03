.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://github.com/scailfin/rob-webapi-flask/blob/master/LICENSE

.. image:: https://github.com/scailfin/flowserv-core/workflows/build/badge.svg
   :target: https://github.com/scailfin/flowserv-core/actions?query=workflow%3A%22build%22


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

    Usage: flowserv init [OPTIONS]

      Initialize database and base directories for the API.

    Options:
      -f, --force  Create database without confirmation
      --help       Show this message and exit.


Create and delete Benchmarks
----------------------------

Create a new benchmark.

.. code-block:: console

    Usage: flowserv workflows create [OPTIONS] TEMPLATE

      Create a new workflow.

    Options:
      -n, --name TEXT          Unique workflow name.
      -d, --description TEXT   Short workflow description.
      -i, --instructions PATH  File containing instructions for running the
                               workflow.

      -f, --specfile FILE      Optional path to workflow specification file.
      -m, --manifest FILE      Optional path to workflow manifest file.
      --help                   Show this message and exit.


Delete a given benchmark.

.. code-block:: console

    Usage: flowserv workflows delete [OPTIONS] IDENTIFIER

      Delete a given workflow.

    Options:
      --help  Show this message and exit.
