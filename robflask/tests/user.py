# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper method for unit tests to create app users."""

import json

import flowserv.config.api as config
import robflask.api.user as user


"""Name of the element in the response that contains the access token."""
USER_TOKEN = 'token'


def create_user(client, username):
    """Create a new user and login the user. The given user name will also be
    used as the user password.

    Returns the user identifier and the access token.

    Parameters
    ----------
    client: flask.app client
        Client for the Flask app
    username: string
        Unique user name

    Returns
    -------
    (string, string)
    """
    data = {
        user.LABEL_NAME: username,
        user.LABEL_PASSWORD: username,
        user.LABEL_VERIFY_USER: False
    }
    r = client.post(config.API_PATH() + '/users/register', json=data)
    user_id = json.loads(r.data)[user.LABEL_ID]
    data = {user.LABEL_NAME: username, user.LABEL_PASSWORD: username}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    token = json.loads(r.data)[USER_TOKEN]
    return user_id, token
