# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test app routes that interact with benchmark submissions and file uploads."""

import io
import json
import os

from robflask.tests import create_user

import robcore.view.labels as labels
import robflask.service as service

DIR = os.path.dirname(os.path.realpath(__file__))
SMALL_FILE = os.path.join(DIR, '../.files/data/names.txt')
LARGE_FILE = os.path.join(DIR, '../.files/data/largefile.txt')


def test_submissions(client, benchmark, url_prefix):
    """Unit tests that create, access, update and delete submissions."""
    # Create common request header that contains the API key
    user_1, token_1 = create_user(client, url_prefix)
    headers = {service.HEADER_TOKEN: token_1}
    # User that is not a submission member
    _, token_inv = create_user(client, url_prefix)
    # Create a new submission.
    benchmark_id = benchmark.identifier
    url = '{}/benchmarks/{}/submissions'.format(url_prefix, benchmark_id)
    body = {labels.NAME: 'First submission'}
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 201
    submission_id = json.loads(r.data)[labels.ID]
    sub_url = '{}/submissions/{}'.format(url_prefix, submission_id)
    # Creating a submission with the same name will return a BAD REQUEST
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 400
    # The submission listing contains one element
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.SUBMISSIONS]) == 1
    r = client.get(sub_url, headers=headers)
    assert r.status_code == 200
    # Create a second user. Initially, the user can access the submission
    # but cannot update it
    user_2, token_2 = create_user(client, url_prefix)
    r = client.get(sub_url, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 200
    body = {
        labels.NAME: 'Submission (updated)',
        labels.MEMBERS: [user_1, user_2]
    }
    r = client.put(sub_url, json=body, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 403
    r = client.put(sub_url, json=body, headers=headers)
    assert r.status_code == 200
    r = client.get(sub_url, headers=headers)
    assert json.loads(r.data)[labels.NAME] == 'Submission (updated)'
    body[labels.NAME] = 'First submission (updated)'
    r = client.put(sub_url, json=body, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 200
    r = client.get(sub_url, headers={service.HEADER_TOKEN: token_2})
    obj = json.loads(r.data)
    assert obj[labels.NAME] == 'First submission (updated)'
    assert len(obj[labels.MEMBERS]) == 2
    # The number of submission each user is a member of is 1
    r = client.get(url_prefix + '/submissions', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.SUBMISSIONS]) == 1
    r = client.get(url_prefix + '/submissions', headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.SUBMISSIONS]) == 1
    # Access submissions with an invalid access token will return FORBIDDEN
    r = client.post(url, json=body, headers={service.HEADER_TOKEN: 'invalid'})
    assert r.status_code == 403
    r = client.get(url, headers={service.HEADER_TOKEN: 'invalid'})
    assert r.status_code == 403
    r = client.delete(sub_url, headers={service.HEADER_TOKEN: token_inv})
    assert r.status_code == 403
    # Delete the submissions
    r = client.delete(sub_url, headers=headers)
    assert r.status_code == 204
    r = client.delete(sub_url, headers=headers)
    assert r.status_code == 404

def test_submission_uploads(client, benchmark, url_prefix):
    """Unit tests that create, access, update and delete submissions."""
    # Create common request header that contains the API key
    user_1, token_1 = create_user(client, url_prefix)
    headers = {service.HEADER_TOKEN: token_1}
    # User that is not a submission member
    _, token_inv = create_user(client, url_prefix)
    # Create a new submission.
    benchmark_id = benchmark.identifier
    url = '{}/benchmarks/{}/submissions'.format(url_prefix, benchmark_id)
    r = client.post(url, json={labels.NAME: 'Submission'}, headers=headers)
    assert r.status_code == 201
    submission_id = json.loads(r.data)[labels.ID]
    # Upload a new file
    data = dict()
    with open(SMALL_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = '{}/submissions/{}/files'.format(url_prefix, submission_id)
    r = client.post(url, data=data, content_type='multipart/form-data', headers=headers)
    assert r.status_code == 201
    file_id = json.loads(r.data)[labels.ID]
    # Attempt to upload a file that is too large
    data = dict()
    with open(LARGE_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = '{}/submissions/{}/files'.format(url_prefix, submission_id)
    r = client.post(url, data=data, content_type='multipart/form-data', headers=headers)
    assert r.status_code == 413
    # The file listing contains one element
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.FILES]) == 1
    # Download the file
    url = '{}/submissions/{}/files/{}'.format(url_prefix, submission_id, file_id)
    r = client.get(url, headers={service.HEADER_TOKEN: token_inv})
    assert r.status_code == 403
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    # Delete the file
    r = client.delete(url, headers={service.HEADER_TOKEN: token_inv})
    assert r.status_code == 403
    r = client.delete(url, headers=headers)
    assert r.status_code == 204
    r = client.delete(url, headers=headers)
    assert r.status_code == 404
    # The lsiting is empty now
    url = '{}/submissions/{}/files'.format(url_prefix, submission_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.FILES]) == 0
