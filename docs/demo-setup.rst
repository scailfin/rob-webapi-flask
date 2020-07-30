==========================
Flask Web API - Demo Setup
==========================

The following step show an example setup of the Web API to run the Reproducible Open Benchmarks for Data Analysis Platform (ROB) Demo benchmarks `Hello World Demo <https://github.com/scailfin/rob-demo-hello-world>`_.


There is a `screen recording of the setup steps <https://asciinema.org/a/285082>`_ available online.



Prerequisites
=============

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


The Flask Web API for ROB requires the ``flowserv`` package. All packages are installable using ``pip``:

..code-block:: bash

    pip install rob-flask
    pip install rob-client


You can also install the packages from the source code on GitHub. The following steps will install all packages from the respective GitHub repositories. You can first clone the repositories and the install the packages that are contained in them:

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



Configure the Environment
=========================

All components of ROB are `configured using environment variables <https://github.com/scailfin/flowserv-core/blob/master/docs/configuration.rst>`_.

Set environment variables to run Flask from the command line:

.. code-block:: bash

    export FLASK_APP=robflask.api
    export FLASK_ENV=development


Configure the ROB API base directory and the workflow controller. In this setup we maintain all files and databases in a local folder ``.rob`` within the current working directory. The ROB Demos use the simple multi-process workflow controller to execute benchmark runs.

.. code-block:: bash

    export FLOWSERV_API_DIR=./.rob
    export FLOWSERV_API_PATH=/rob/api/v1
    export FLOWSERV_BACKEND_CLASS=SerialWorkflowEngine
    export FLOWSERV_BACKEND_MODULE=flowserv.controller.serial.engine


ROB currently supports two database management systems. This example uses a SQLite3 database to maintain benchmark information. The database will be maintained as file ``db.sqlite`` in the current working directory.

.. code-block:: bash

    export FLOWSERV_DATABASE=sqlite:///./db.sqlite
    


Create the Database
===================

The Web API includes a command line tool to initialize database and base directories that are used by the  Web API to store information about users, benchmarks, user submissions, benchmark results.

.. code-block:: bash

    flowserv init


Install the Hello World Demo
============================

The *Hello World Demo* can be installed from the **flowServ** workflow repository using the following command:

.. code-block:: bash

    flowserv install helloworld
    
Note: You can use the command ``flowserv repository`` to get a complete list of all available workflow templates.


Run the Web Server
==================

After setting everything up you can run the Flask Web Server using the following command:

.. code-block:: bash

    flask run
    
    
Register a new User
===================

The ROB User Interface is currently in an experimental state. Before being able to use the interface open a new termainal window (in the same working directory) as the terminal that is running the Flask server. The following steps will allow you to register a new user with ROB:

.. code-block:: bash

    # Activate the virutal environment
    source venv/bin/activate
    # Set API path variable
    export FLOWSERV_API_PATH=/rob/api/v1
    # Register user (follow prompts to enter user name and password)
    rob register
    
 After you have registered the user, you can clone and run the ROB user interface.
 
 .. code-block:: bash
 
    git clone git@github.com:scailfin/rob-ui.git
    cd rob-ui
    npm start
