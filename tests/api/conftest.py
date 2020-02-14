# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Initialize the app client for unit tests. Follwos the example in
https://github.com/pallets/flask/tree/master/examples/tutorial/tests
"""

import os
import shutil
import tempfile

import pytest

from flowserv.config.api import FLOWSERV_API_BASEDIR
from flowserv.config.db import FLOWSERV_DB_ID
from flowserv.config.install import DB
from robflask.api import create_app
from robflask.service.base import service

import flowserv.core.db.driver as driver
import flowserv.core.db.sqlite as sqlite
import robflask.config as config


DIR = os.path.dirname(os.path.realpath(__file__))
BENCHMARK_DIR = os.path.join(DIR, '../.files/helloworld')


@pytest.fixture
def client():
    """Create the app client."""
    # Create a temporary file to use as the database file
    basedir = tempfile.mkdtemp()
    db_filename = os.path.join(basedir, 'db.sqlite')
    # The test database uses SQLite
    os.environ[FLOWSERV_API_BASEDIR] = basedir
    os.environ[FLOWSERV_DB_ID] = driver.SQLITE[0]
    os.environ[sqlite.SQLITE_FLOWSERV_CONNECT] = db_filename
    DB.init()
    # Create a single benchmark
    with service() as api:
        # Get the benchmark repository instance from the API
        api.workflows().create_workflow(
            name='Hello World',
            description='Hello World Demo',
            sourcedir=BENCHMARK_DIR
        )
    # Set the maximum upload file size to 1KB
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = '1024'
    # Create the Flask app
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client
    # Clean up deletes the database file
    shutil.rmtree(basedir)
