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

from flowserv.model.database import DB, TEST_DB

import robflask.config as config


DIR = os.path.dirname(os.path.realpath(__file__))
BENCHMARK_DIR = os.path.join(DIR, '../.files/helloworld')
ROB_UI_PATH = os.path.join(DIR, '../../resources/ui')


@pytest.fixture
def benchmark_id():
    """Identifier for the created test benchmark."""
    return 'helloworld'


@pytest.fixture
def client(benchmark_id, tmpdir):
    """Create the app client."""
    # Set the environment variables and create the database.
    connect_url = TEST_DB(tmpdir)
    DB(connect_url=connect_url).init()
    # Create a single benchmark. Need to ensure that the API factory points to
    # the newly created database.
    from robflask.service import init_service
    init_service(basedir=tmpdir, database=connect_url)
    from robflask.service import service
    with service() as api:
        # Get the benchmark repository instance from the API
        api.workflows().create_workflow(
            identifier=benchmark_id,
            name='Hello World',
            description='Hello World Demo',
            source=BENCHMARK_DIR
        )
    # Set the maximum upload file size to 1KB
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = '1024'
    # Set the UI path.
    os.environ[config.ROB_UI_PATH] = ROB_UI_PATH
    # Create the Flask app
    from robflask.api import create_app
    app = create_app({'TESTING': True})
    with app.test_client() as client:
        yield client
