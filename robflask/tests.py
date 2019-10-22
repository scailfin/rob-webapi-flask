# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper methods for unit tests."""

import json

import robcore.util as util
import robcore.view.labels as labels


def create_user(client, url_prefix):
    """Create a new user with a unique name. The user is logged in afterwards.
    Returns the user identifier and the access token.

    Parameters
    ----------
    client: flask client
        Flask application client
    url_prefix: string
        Prefix for application routes

    Returns
    -------
    string, string
    """
    # Create an active user with a unique user name
    user_name = util.get_unique_identifier()
    body = {
        labels.USERNAME: user_name,
        labels.PASSWORD: 'pwd',
        labels.VERIFY_USER: False
    }
    client.post(url_prefix + '/users/register', json=body)
    login = {labels.USERNAME: user_name, labels.PASSWORD: 'pwd'}
    r = client.post(url_prefix + '/users/login', json=login)
    obj = json.loads(r.data)
    return obj[labels.ID], obj[labels.ACCESS_TOKEN]
