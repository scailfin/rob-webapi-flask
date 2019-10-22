# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test service descriptor route of the flask app."""

import json

from robflask.version import __version__

import robcore.view.labels as labels


def test_service_descriptor(client, url_prefix):
    """Get service descriptor and ensure that the version is set correclty."""
    r = client.get(url_prefix + '/')
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert obj[labels.VERSION] == __version__
