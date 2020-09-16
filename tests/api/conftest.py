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

import pytest

from flowserv.config.api import FLOWSERV_API_BASEDIR
from flowserv.config.database import FLOWSERV_DB

import robflask.config as config


DIR = os.path.dirname(os.path.realpath(__file__))
BENCHMARK_DIR = os.path.join(DIR, '../.files/helloworld')


@pytest.fixture
def client(tmpdir):
    """Create the app client."""
    # Create a temporary file to use as the database file
    os.environ[FLOWSERV_DB] = 'sqlite:///{}/flowserv.db'.format(str(tmpdir))
    os.environ[FLOWSERV_API_BASEDIR] = str(tmpdir)
    from flowserv.service.database import database
    database.init()
    # Create a single benchmark
    from robflask.service.base import service
    with service() as api:
        # Get the benchmark repository instance from the API
        api.workflows().create_workflow(
            name='Hello World',
            description='Hello World Demo',
            source=BENCHMARK_DIR
        )
        # Need to set the file store in the engine and the backend to the new
        # instance that refers to the current tmpdir.
        from flowserv.service.files import get_filestore
        api.engine.fs = get_filestore()
        from flowserv.service.backend import backend
        backend.fs = api.engine.fs
    # Set the maximum upload file size to 1KB
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = '1024'
    # Create the Flask app
    from robflask.api import create_app
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client
