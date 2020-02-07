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

import json

from robflask.api.auth import HEADER_TOKEN
from robflask.tests.user import create_user

import flowserv.config.api as config
import robflask.tests.serialize as serialize


def test_benchmarks(client):
    """Unit tests that list and access available benchmarks."""
    # Create user and the request header that contains the API key for the
    # logged in user.
    _, token = create_user(client, '0000')
    headers = {HEADER_TOKEN: token}
    # The benchmark listing contains one element
    r = client.get(config.API_PATH() + '/benchmarks', headers=headers)
    assert r.status_code == 200
    benchmarks = json.loads(r.data)
    serialize.validate_benchmark_listing(benchmarks)
    assert len(benchmarks['benchmarks']) == 1
    benchmark_id = benchmarks['benchmarks'][0]['id']
    # Access the benchmark handle
    url = config.API_PATH() + '/benchmarks/{}'.format(benchmark_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    benchmark = json.loads(r.data)
    serialize.validate_benchmark_handle(benchmark)
    assert benchmark['id'] == benchmark_id
    # Attempt to access unknown benchmark
    url = config.API_PATH() + '/benchmarks/undefined'
    r = client.get(url, headers=headers)
    assert r.status_code == 404
