# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test app routes that interact with benchmark submissions and file uploads.
"""

import io
import json
import os

from robflask.api.util import HEADER_TOKEN
from robflask.tests.benchmark import get_benchmark
from robflask.tests.submission import create_submission
from robflask.tests.user import create_user

import flowserv.config.api as config
import robflask.tests.serialize as serialize


DIR = os.path.dirname(os.path.realpath(__file__))
SMALL_FILE = os.path.join(DIR, '../.files/data/names.txt')
LARGE_FILE = os.path.join(DIR, '../.files/data/largefile.txt')


"""Url patterns."""
ACCESS_SUBMISSION = '{}/submissions/{}'
CREATE_SUBMISSION = '{}/benchmarks/{}/submissions'
SUBMISSION_LIST = '{}/submissions'
SUBMISSION_FILES = '{}/submissions/{}/files'
SUBMISSION_FILE = '{}/submissions/{}/files/{}'


def test_submission_life_cycle(client):
    """Unit tests that create, access, list, update, and delete submissions."""
    # Create user and the request header that contains the API key for the
    # logged in user.
    user_1, token_1 = create_user(client, '0000')
    headers_1 = {HEADER_TOKEN: token_1}
    # Get the identifier of the default benchmark
    b_id = get_benchmark(client)
    # -- Create submission ----------------------------------------------------
    url = CREATE_SUBMISSION.format(config.API_PATH(), b_id)
    body = {'name': 'First submission'}
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 201
    submission = json.loads(r.data)
    serialize.validate_submission_handle(submission)
    s_id = submission['id']
    # Creating a submission with the same name will return a BAD REQUEST
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 400
    # Creating a submission with an unknown member will return a BAD REQUEST
    err_body = {'name': 'Error submission', 'members': ['ABCD']}
    r = client.post(url, json=err_body, headers=headers_1)
    assert r.status_code == 400
    # -- Retrieve submission --------------------------------------------------
    url = ACCESS_SUBMISSION.format(config.API_PATH(), s_id)
    r = client.get(url, headers=headers_1)
    submission = json.loads(r.data)
    serialize.validate_submission_handle(submission)
    # -- List submissions -----------------------------------------------------
    url = CREATE_SUBMISSION.format(config.API_PATH(), b_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    submissions = json.loads(r.data)
    serialize.validate_submission_listing(submissions)
    assert len(submissions['submissions']) == 1
    # -- Update submission ----------------------------------------------------
    # Create a second user.
    user_2, token_2 = create_user(client, '0001')
    headers_2 = {HEADER_TOKEN: token_2}
    url = ACCESS_SUBMISSION.format(config.API_PATH(), s_id)
    body = {'name': 'Submission (updated)', 'members': [user_1, user_2]}
    # Initially the new user can retrieve the submission but not update it
    r = client.get(url, headers=headers_2)
    assert r.status_code == 200
    r = client.put(url, json=body, headers=headers_2)
    assert r.status_code == 403
    # The owner of the submission can update it
    r = client.put(url, json=body, headers=headers_1)
    assert r.status_code == 200
    submission = json.loads(r.data)
    serialize.validate_submission_handle(submission)
    assert submission['name'] == 'Submission (updated)'
    # Now the second user can access the submission
    r = client.get(url, headers=headers_2)
    assert r.status_code == 200
    submission = json.loads(r.data)
    serialize.validate_submission_handle(submission)
    assert submission['name'] == 'Submission (updated)'
    # THe new member can also update the submission
    body = {'name': 'First submission (updated)'}
    r = client.put(url, json=body, headers=headers_2)
    assert r.status_code == 200
    r = client.get(url, headers=headers_2)
    submission = json.loads(r.data)
    serialize.validate_submission_handle(submission)
    assert submission['name'] == 'First submission (updated)'
    # The number of submission each user is a member of is 1
    url = SUBMISSION_LIST.format(config.API_PATH())
    for headers in [headers_1, headers_2]:
        r = client.get(url, headers=headers)
        assert r.status_code == 200
        assert len(json.loads(r.data)['submissions']) == 1
    # Access submissions with an invalid access token will return FORBIDDEN
    # Create submission
    url = CREATE_SUBMISSION.format(config.API_PATH(), b_id)
    r = client.post(url, json={'name': 'S'}, headers={HEADER_TOKEN: 'invalid'})
    assert r.status_code == 403
    # Submission listing
    url = SUBMISSION_LIST.format(config.API_PATH())
    r = client.get(url, headers={HEADER_TOKEN: 'invalid'})
    # Update submission
    url = ACCESS_SUBMISSION.format(config.API_PATH(), s_id)
    r = client.put(url, json=body, headers={HEADER_TOKEN: 'invalid'})
    assert r.status_code == 403
    # -- Delete submission ----------------------------------------------------
    url = ACCESS_SUBMISSION.format(config.API_PATH(), s_id)
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 204
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 404


def test_submission_uploads(client):
    """Unit tests that upload files for submissions."""
    # Create user and submission.
    s_id, headers_1, headers_2 = create_submission(client)
    # Upload a new file
    data = dict()
    with open(SMALL_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = SUBMISSION_FILES.format(config.API_PATH(), s_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers_1
    )
    assert r.status_code == 201
    file_id = json.loads(r.data)['id']
    # Attempt to upload a file that is too large
    data = dict()
    with open(LARGE_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = SUBMISSION_FILES.format(config.API_PATH(), s_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers_1
    )
    assert r.status_code == 413
    # The file listing contains one element
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    assert len(json.loads(r.data)['files']) == 1
    # Download the file
    url = SUBMISSION_FILE.format(config.API_PATH(), s_id, file_id)
    r = client.get(url, headers=headers_2)
    assert r.status_code == 403
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    # Delete the file
    r = client.delete(url, headers=headers_2)
    assert r.status_code == 403
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 204
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 404
    # The lsiting is empty now
    url = SUBMISSION_FILES.format(config.API_PATH(), s_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    assert len(json.loads(r.data)['files']) == 0
