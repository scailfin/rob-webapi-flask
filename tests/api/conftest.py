# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Initialize the app client for unit tests. Follwos the example in
https://github.com/pallets/flask/tree/master/examples/tutorial/tests
"""

import os
import tempfile

import pytest

from robcore.config.install import DB
from robflask.service import service

import robcore.config.api as apiconf
import robcore.config.db as dbconf
import robcore.db.driver as dbdriver
import robcore.db.sqlite as sqlite
import robflask.api as api
import robflask.config as config


DIR = os.path.dirname(os.path.realpath(__file__))
BENCHMARK_DIR = os.path.join(DIR, '../.files/helloworld')


@pytest.fixture
def benchmark():
    """Create the default 'Hello World' benchmark."""
    with service() as api:
        # Get the benchmark repository instance from the API
        repo = api.benchmark_repository()
        b = repo.add_benchmark(
            name='Hello World',
            description='Hello World Demo',
            src_dir=BENCHMARK_DIR
        )
        return b


@pytest.fixture
def client():
    """Create the app client."""
    # Create a temporary file to use as the database file
    db_fd, db_filename = tempfile.mkstemp()
    # The test database uses SQLite
    os.environ[dbconf.ROB_DB_ID] = dbdriver.SQLITE[0]
    os.environ[sqlite.SQLITE_ROB_CONNECT] = db_filename
    DB.init()
    # Set the maximum upload file size to 1KB
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = '1024'
    # Create the Flask app
    app = api.create_app({'TESTING': True})
    with app.test_client() as client:
        yield client
    # Clean up deletes the database file
    os.close(db_fd)
    os.unlink(db_filename)


@pytest.fixture
def url_prefix():
    """Prefix for all application routes."""
    return apiconf.API_PATH()
