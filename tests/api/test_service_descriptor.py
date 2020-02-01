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

import flowserv.config.api as config
import flowserv.tests.serialize as serialize


def test_service_descriptor(client):
    """Get service descriptor and ensure that the version is set correclty."""
    r = client.get(config.API_PATH() + '/')
    assert r.status_code == 200
    obj = json.loads(r.data)
    serialize.validate_service_descriptor(obj)
    assert obj['version'] == __version__
