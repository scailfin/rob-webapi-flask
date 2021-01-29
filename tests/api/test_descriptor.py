# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test service descriptor route of the flask app."""

import robflask.config as config


def test_service_descriptor(client):
    """Get service descriptor and ensure that the version is set correclty."""
    r = client.get(config.API_PATH() + '/')
    assert r.status_code == 200
