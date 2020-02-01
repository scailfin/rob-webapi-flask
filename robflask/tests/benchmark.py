# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper method for unit tests that access the default benchmark."""

import json

import flowserv.config.api as config


def get_benchmark(client):
    """Get the identifier of the banchmark that has been created when the
    service was instantiated.

    Parameters
    ----------
    client: flask.app client
        Client for the Flask app

    Returns
    -------
    string
    """
    r = client.get(config.API_PATH() + '/benchmarks')
    benchmarks = json.loads(r.data)
    return benchmarks['benchmarks'][0]['id']
