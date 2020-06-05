==========================
Flask Web API - Demo Setup
==========================

The following step show an example setup of the Web API to run the Reproducible Open Benchmarks for Data Analysis Platform (ROB) Demo benchmarks `Hello World Demo <https://github.com/scailfin/rob-demo-hello-world>`_ and `Number Predictor Demo <https://github.com/scailfin/rob-demo-predictor>`_.


There is a `screen recording of the setup steps <https://asciinema.org/a/285082>`_ available online.



Prerequisites
=============

We recommend using a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for the installation. The following steps will create and activate a new virtual environment in the current working directory.

.. code-block:: bash

    # -- Create a new virtual environment
    virtualenv venv
    # -- Activate the virtual environment
    source venv/bin/activate


The Flask Web API for ROB requires the ``robcore`` package. The following steps will install all packages from the respective GitHub repositories:

    .. code-block:: bash

        # Clone repositories and install locally
        git clone git@github.com:scailfin/flowserv-core.git
        pip install -e flowserv-core
        git clone git@github.com:scailfin/rob-webapi-flask.git
        pip install -e rob-webapi-flask
        
        # Alternatively: Install directly from GitHub repository
        pip install git+https://github.com/scailfin/flowserv-core.git
        pip install git+https://github.com/scailfin/rob-webapi-flask.git



Configure the Environment
=========================

All components of ROB are `configured using environment variables <https://github.com/scailfin/flowserv-core/blob/master/docs/configuration.rst>`_.

Set environment variables to run Flask from the command line:

.. code-block:: bash

    export FLASK_APP=robflask.api
    export FLASK_ENV=development


Configure the ROB API base directory and the workflow controller. In this setup we maintain all files and databases in a local folder ``.rob`` within the current working directory. The ROB Demos use the simple multi-process workflow controller to execute benchmark runs.

.. code-block:: bash

    export ROB_API_DIR=./.rob
    export ROB_ENGINE_CLASS=MultiProcessWorkflowEngine
    export ROB_ENGINE_MODULE=robcore.controller.backend.multiproc


ROB currently supports two database management systems. This example uses a SQLite3 database to maintain benchmark information. The database will be maintained as file ``db.sqlite`` in the API base folder.

.. code-block:: bash

    export ROB_DBMS=SQLITE3
    export SQLITE_ROB_CONNECT=./.rob/db.sqlite


Create the Database
===================

The Web API includes a command line tool to initialize database and base directories that are used by the  Web API to store information about users, benchmarks, user submissions, benchmark results.

.. code-block:: bash

    robadm init



Run the Web Server
==================

After setting everything up you can run the Flask Web Server using the following command:

.. code-block:: bash

    flask run
