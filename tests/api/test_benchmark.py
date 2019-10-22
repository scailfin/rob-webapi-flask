# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test app routes that retrieve benchmark listings and benchamrk handles."""

import json

from robflask.tests import create_user

import robcore.view.labels as labels
import robflask.service as service


def test_benchmarks(client, benchmark, url_prefix):
    """Unit tests that list and access available benchmarks."""
    # Create ucommon request header that contains the API key
    user_id, token = create_user(client, url_prefix)
    headers = {service.HEADER_TOKEN: token}
    # The benchmark listing contains one element
    r = client.get(url_prefix + '/benchmarks', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.BENCHMARKS]) == 1
    # Access the benchmark handle
    url = url_prefix + '/benchmarks/{}'.format(benchmark.identifier)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    assert json.loads(r.data)[labels.ID] == benchmark.identifier
    # Attempt to access unknown benchmark
    url = url_prefix + '/benchmarks/undefined'
    r = client.get(url, headers=headers)
    assert r.status_code == 404
