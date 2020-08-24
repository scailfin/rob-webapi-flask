==========================
Flask Web API - Demo Setup
==========================

The following steps show an example setup of the Web API to run the Reproducible Open Benchmarks for Data Analysis Platform (ROB) Demo benchmarks `Hello World Demo <https://github.com/scailfin/rob-demo-hello-world>`_. The steps assume that your working directory is ``/home/user/project/rob``. Make sure to adjust all path names to your local environment.


There is also a `slide deck with step-by-step instructions <https://github.com/scailfin/rob-webapi-flask/blob/master/docs/slides/ROB-Demo-Setup.pdf>`_.



Installation
============

Virtual Environment
-------------------

We recommend using a `virtual environment <https://virtualenv.pypa.io/en/stable/>`_ for the installation. The following steps will create and activate a new virtual environment in the current working directory.

.. code-block:: bash

    # -- Create a new virtual environment
    virtualenv venv
    # -- Activate the virtual environment
    source venv/bin/activate

If you are using the Python distribution from `Anaconda <https://www.anaconda.com/>`_, you can setup an environment like this:

.. code-block:: bash

    # -- Create a new virtual environment
    conda create -n rob pip
    # -- Activate the virtual environment
    conda activate rob


Install Packages
----------------

The Flask Web API for ROB requires the `flowserv package <https://github.com/scailfin/flowserv-core>`_. If you want to run the demo from the command line you also need to install the `rob-client package <https://github.com/scailfin/rob-client>`_. All packages are installable from the source code on GitHub using ``pip``.

The following steps will install all packages from the respective GitHub repositories. You can first clone the repositories and the install the packages that are contained in them:

.. code-block:: bash

    # Clone repositories and install locally
    git clone git@github.com:scailfin/flowserv-core.git
    pip install -e flowserv-core
    git clone git@github.com:scailfin/rob-webapi-flask.git
    pip install -e rob-webapi-flask
    # Optional, install the ROB API command line interface
    git clone git@github.com:scailfin/rob-client.git
    pip install -e rob-client


Alternatively, you can install the packages directly from the respective GitHub repositories:

.. code-block:: bash

    pip install git+https://github.com/scailfin/flowserv-core.git
    pip install git+https://github.com/scailfin/rob-webapi-flask.git
    # Optional, install the ROB API command line interface
    pip install git+https://github.com/scailfin/rob-client.git



Configuration
=============

All components of ROB are `configured using environment variables <https://github.com/scailfin/flowserv-core/blob/master/docs/configuration.rst>`_.


Database
--------

Ensure that the following environment variables are set before starting the demo server. This example uses SQLite. For more examples, see the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls>`_.

.. code-block:: bash

    export FLOWSERV_DATABASE=sqlite:////home/user/project/rob/db.sqlite


Directory for Benchmark Runs
----------------------------

Configure the ROB API base directory and the workflow controller. In this setup we maintain all files and databases in a local folder ``.rob`` within the current working directory. The ROB Demos use the simple multi-process workflow controller to execute benchmark runs.

.. code-block:: bash

    export FLOWSERV_API_DIR=/home/user/project/rob/.rob
    export FLOWSERV_API_PATH=/rob/api/v1


ROB User-Interface
------------------

The ROB Web API package contains a build of the `ROB User-Interface <https://github.com/scailfin/rob-ui>`_. For the Flask server to be able to serve the UI files, you need to set the following environment variable.

.. code-block:: bash

    export ROB_UI_PATH=/home/user/project/rob/rob-webapi-flask/resources/ui


Setup Database & Install Demo
=============================

The Web API includes a command line tool to initialize database and base directories that are used by the  Web API to store information about users, benchmarks, user submissions, benchmark results.

.. code-block:: bash

    flowserv init


To run the demo you need to register at least one user.

.. code-block:: bash

    flowserv register -u alice -p abc123


The next step is to install the code for the demo workflows. The example below is for the `Hello World Demo <https://github.com/scailfin/rob-demo-hello-world>`_. Use ``flowserv repository`` to get a list of currently available benchmarks.

.. code-block:: bash

    flowserv install helloworld


Run the Demo
============

Before you start the Flask Web server the workflow engine needs to be defined. The settings differ for the two demos. Note that **Hello World** can run with the same settings as **Top Tagger** but **Top Tagger** cannot run with **Hello World** settings (unless you install the **Top tagger** code manually in your virtual environment).

Set environment variables for the **Hello World** Demo:

.. code-block:: bash

    export FLOWSERV_BACKEND_MODULE=flowserv.controller.serial.engine
    export FLOWSERV_BACKEND_CLASS=SerialWorkflowEngine


Set environment variables for the **Top Tagger** Demo:

.. code-block:: bash

    # Note that this demo requires a running Docker Daemon on your machine.
    export FLOWSERV_BACKEND_MODULE=flowserv.controller.serial.docker
    export FLOWSERV_BACKEND_CLASS=DockerWorkflowEngine


Set environment variables to run the Flask development server. The Web UI should then be available at `http://127.0.0.1:5000/rob-ui/`.

.. code-block:: bash

    export FLASK_APP=robflask.api
    export FLASK_ENV=development

    flask run


Run Demo from Command Line
--------------------------

If you want to run the demo from the command-line instead, you need to open an new terminal window. Make sure to activate the virtual environment and set the environment variable FLOWSERV_API_PATH to the same value as in the terminal that is running the Flask server.

.. code-block:: bash

    export FLOWSERV_API_PATH=/rob/api/v1
