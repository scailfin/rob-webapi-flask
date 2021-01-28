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
import os

from robflask.tests.user import create_user
from robflask.api.util import HEADER_TOKEN

import flowserv.view.files as flbls
import flowserv.view.group as labels
import robflask.config as config


DIR = os.path.dirname(os.path.realpath(__file__))
SMALL_FILE = os.path.join(DIR, '../.files/data/names.txt')
LARGE_FILE = os.path.join(DIR, '../.files/data/largefile.txt')


"""Url patterns."""
CREATE_SUBMISSION = '{}/workflows/{}/groups'
SUBMISSION_FILES = '{}/uploads/{}/files'
SUBMISSION_FILE = '{}/uploads/{}/files/{}'


def test_submission_uploads(client, benchmark_id):
    """Tests uploading and retrieving a file."""
    # -- Setup ----------------------------------------------------------------
    # Create new user and submission.
    user_1, token_1 = create_user(client, '0000')
    headers = {HEADER_TOKEN: token_1}
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={labels.GROUP_NAME: 'S1'}, headers=headers)
    submission_id = r.json[labels.GROUP_ID]
    # -- Upload files ---------------------------------------------------------
    data = dict()
    with open(SMALL_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers
    )
    assert r.status_code == 201
    file_id = r.json[flbls.FILE_ID]
    # Attempt to upload a file that is too large
    data = dict()
    with open(LARGE_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers
    )
    assert r.status_code == 413
    # Download the file.
    url = SUBMISSION_FILE.format(config.API_PATH(), submission_id, file_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    assert b'Alice' in r.data
    assert b'Bob' in r.data
    # -- Error cases ----------------------------------------------------------
    data = {'file': (io.BytesIO(b'Alice'), '')}
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.post(url, data=data, content_type='multipart/form-data', headers=headers)
    assert r.status_code == 400
    data = {}
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.post(url, data=data, content_type='multipart/form-data', headers=headers)
    assert r.status_code == 400


def test_uploads_listings(client, benchmark_id):
    """Tests uploading and retrieving a file."""
    # -- Setup ----------------------------------------------------------------
    # Create new user and submission. Then upload a single file.
    user_1, token_1 = create_user(client, '0000')
    headers = {HEADER_TOKEN: token_1}
    url = CREATE_SUBMISSION.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={labels.GROUP_NAME: 'S1'}, headers=headers)
    submission_id = r.json[labels.GROUP_ID]
    data = dict()
    with open(SMALL_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers
    )
    assert r.status_code == 201
    file_id = r.json[flbls.FILE_ID]
    # -- Listing uploaded files -----------------------------------------------
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    doc = r.json
    assert len(doc[flbls.FILE_LIST]) == 1
    # Delete the file.
    url = SUBMISSION_FILE.format(config.API_PATH(), submission_id, file_id)
    r = client.delete(url, headers=headers)
    assert r.status_code == 204
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    doc = r.json
    assert len(doc[flbls.FILE_LIST]) == 0
