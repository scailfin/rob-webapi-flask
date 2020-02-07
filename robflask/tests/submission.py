# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper method for unit tests that use benchmark submissions."""

import io
import json

from robflask.api.auth import HEADER_TOKEN
from robflask.tests.benchmark import get_benchmark
from robflask.tests.user import create_user

import flowserv.config.api as config


def create_submission(client):
    """Create a new submission for the default benchmark. Also creates two
    users that are logged in. The first user is a member of the submission and
    the second user is not.

    Returns the identifier for the new submissions and the request headers
    for both users.

    Parameters
    ----------
    client: flask.app client
        Client for the Flask app

    Returns
    -------
    string, dict, dict
    """
    user_1, token_1 = create_user(client, '0000')
    headers_1 = {HEADER_TOKEN: token_1}
    # User that is not a submission member
    user_2, token_2 = create_user(client, '0001')
    headers_2 = {HEADER_TOKEN: token_2}
    # Create a new submission.
    b_id = get_benchmark(client)
    url = '{}/benchmarks/{}/submissions'.format(config.API_PATH(), b_id)
    body = {'name': 'First submission'}
    r = client.post(url, json=body, headers=headers_1)
    submission = json.loads(r.data)
    s_id = submission['id']
    return s_id, headers_1, headers_2


def upload_file(client, submission_id, headers, filename):
    """Upload a given file for a submisssion. Returns the identifier of the
    uploaded file.

    Parameters
    ----------
    client: flask.app client
        Client for the Flask app
    submission_id: string
        Unique submission identifier
    headers: dict
        Request header for the submission owner
    filename: string
        Path to the upload file

    -------
    string
    """
    data = dict()
    with open(filename, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = '{}/submissions/{}/files'.format(config.API_PATH(), submission_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers
    )
    assert r.status_code == 201
    return json.loads(r.data)['id']
