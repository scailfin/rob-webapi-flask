# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit test for app routes that retrieve benchmark listings and benchamrk
handles.
"""

from robflask.tests.user import create_user
from robflask.api.util import HEADER_TOKEN

import flowserv.view.workflow as labels
import robflask.config as config


def test_get_benchmark(client, benchmark_id):
    """Test getting a benchmark handle."""
    url = config.API_PATH() + '/workflows/{}'.format(benchmark_id)
    r = client.get(url)
    assert r.status_code == 200
    # Attempt to access unknown benchmark
    url = config.API_PATH() + '/workflows/undefined'
    r = client.get(url)
    assert r.status_code == 404


def test_list_benchmarks(client):
    """Test getting a list of available workflows."""
    # The benchmark listing contains one element (independently of whether the
    # user is logged in or not).
    r = client.get(config.API_PATH() + '/workflows')
    assert r.status_code == 200
    doc = r.json
    assert len(doc[labels.WORKFLOW_LIST]) == 1
    # Create user and the request header that contains the API key for the
    # logged in user.
    _, token = create_user(client, '0000')
    headers = {HEADER_TOKEN: token}
    r = client.get(config.API_PATH() + '/workflows', headers=headers)
    assert r.status_code == 200
    doc = r.json
    assert len(doc[labels.WORKFLOW_LIST]) == 1
