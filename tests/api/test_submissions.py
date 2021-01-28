# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test app routes that interact with benchmark submissions and file uploads.
"""

from robflask.tests.user import create_user
from robflask.api.util import HEADER_TOKEN

import flowserv.view.group as labels
import robflask.config as config


"""Url patterns."""
ACCESS_SUBMISSION = '{}/groups/{}'
CREATE_SUBMISSION = '{}/workflows/{}/groups'
DELETE_SUBMISSION = '{}/groups/{}'
UPDATE_SUBMISSION = '{}/groups/{}'
SUBMISSION_LIST = '{}/workflows/{}/groups'


def test_create_submission(client, benchmark_id):
    """Unit tests that create a new submission."""
    # Create user and the request header that contains the API key for the
    # logged in user.
    user_1, token_1 = create_user(client, '0000')
    headers_1 = {HEADER_TOKEN: token_1}
    # -- Create submission ----------------------------------------------------
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    body = {labels.GROUP_NAME: 'First submission'}
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 201
    # Creating a submission with the same name will return a BAD REQUEST
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 400
    # Creating a submission with an unknown member will return a BAD REQUEST
    err_body = {labels.GROUP_NAME: 'Error submission', labels.GROUP_MEMBERS: ['unknown']}
    r = client.post(url, json=err_body, headers=headers_1)
    assert r.status_code == 400
    # Invalid request when group members is not a list.
    err_body = {labels.GROUP_NAME: 'Error submission', labels.GROUP_MEMBERS: 'unknown'}
    r = client.post(url, json=err_body, headers=headers_1)
    assert r.status_code == 400


def test_delete_submission(client, benchmark_id):
    """Test deleting a previously created submission."""
    # -- Setup ----------------------------------------------------------------
    # Create two users that are logged in.
    user_1, token_1 = create_user(client, '0000')
    user_2, token_2 = create_user(client, '0001')
    headers_1 = {HEADER_TOKEN: token_1}
    headers_2 = {HEADER_TOKEN: token_2}
    # Create one submission for user 1.
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={labels.GROUP_NAME: 'S1'}, headers=headers_1)
    submission_id = r.json[labels.GROUP_ID]
    # -- Delete submission ----------------------------------------------------
    url = ACCESS_SUBMISSION.format(config.API_PATH(), submission_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    # User 2 cannot delete the submission.
    url = DELETE_SUBMISSION.format(config.API_PATH(), submission_id)
    r = client.delete(url, headers=headers_2)
    assert r.status_code == 403
    # User 1 can delete the submission.
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 204
    # Deleting an unknown submission results in statis 404
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 404


def test_get_submission(client, benchmark_id):
    """Unit test to retrieve the handle for a user submission."""
    # -- Setup ----------------------------------------------------------------
    # Create user and the request header that contains the API key for the
    # logged in user.
    user_1, token_1 = create_user(client, '0000')
    headers_1 = {HEADER_TOKEN: token_1}
    # Create submission and get the submission identifier.
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={labels.GROUP_NAME: 'My submission'}, headers=headers_1)
    submission_id = r.json[labels.GROUP_ID]
    # -- Retrieve submission handles ------------------------------------------
    url = ACCESS_SUBMISSION.format(config.API_PATH(), submission_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    # Retureving an unknown submission results in stats 404.
    url = ACCESS_SUBMISSION.format(config.API_PATH(), 'unknown')
    r = client.get(url, headers=headers_1)
    assert r.status_code == 404


def test_list_submissions(client, benchmark_id):
    """Test to retrieve a list of submissions that a user is a member of."""
    # -- Setup ----------------------------------------------------------------
    # Create two users that are logged in.
    user_1, token_1 = create_user(client, '0000')
    user_2, token_2 = create_user(client, '0001')
    headers_1 = {HEADER_TOKEN: token_1}
    headers_2 = {HEADER_TOKEN: token_2}
    # Create two submissions. User 1 is member of both submissions but user 2
    # is only a member of one submission.
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    client.post(url, json={labels.GROUP_NAME: 'S1'}, headers=headers_1)
    client.post(url, json={labels.GROUP_NAME: 'S2', labels.GROUP_MEMBERS: [user_1]}, headers=headers_2)
    # -- Retrieve submission listings ------------------------------------------
    url = SUBMISSION_LIST.format(config.API_PATH(), benchmark_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    doc = r.json
    assert len(doc[labels.GROUP_LIST]) == 2
    # Retureving an unknown submission results in stats 404.
    r = client.get(url, headers=headers_2)
    assert r.status_code == 200
    doc = r.json
    assert len(doc[labels.GROUP_LIST]) == 1


def test_update_submission(client, benchmark_id):
    """Test updating properties of a submission."""
    # -- Setup ----------------------------------------------------------------
    # Create two users that are logged in.
    user_1, token_1 = create_user(client, '0000')
    user_2, token_2 = create_user(client, '0001')
    headers_1 = {HEADER_TOKEN: token_1}
    headers_2 = {HEADER_TOKEN: token_2}
    # Create one submission for user 1.
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={labels.GROUP_NAME: 'S1'}, headers=headers_1)
    submission_id = r.json[labels.GROUP_ID]
    # -- Update submission ----------------------------------------------------
    url = UPDATE_SUBMISSION.format(config.API_PATH(), submission_id)
    body = {labels.GROUP_NAME: 'S1 (updated)'}
    r = client.put(url, json=body, headers=headers_2)
    assert r.status_code == 403
    r = client.put(url, json=body, headers=headers_1)
    assert r.status_code == 200
    assert r.json[labels.GROUP_NAME] == 'S1 (updated)'
    # After adding user 2 as a member they can update the submission as well.
    body = {labels.GROUP_MEMBERS: [user_1, user_2]}
    r = client.put(url, json=body, headers=headers_1)
    assert r.status_code == 200
    body = {labels.GROUP_NAME: 'S1 (new)'}
    r = client.put(url, json=body, headers=headers_2)
    assert r.status_code == 200
    assert r.json[labels.GROUP_NAME] == 'S1 (new)'
