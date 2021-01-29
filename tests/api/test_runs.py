# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019-2021 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Unit tests that start, query and delete runs via the Web API."""

import io
import pytest
import time

from flowserv.service.run.argument import serialize_fh
from robflask.api.util import HEADER_TOKEN
from robflask.tests.user import create_user

import flowserv.model.workflow.state as st
import flowserv.view.files as flbls
import flowserv.view.group as glbls
import flowserv.view.run as rlbls
import robflask.config as config


"""Url patterns."""
BENCHMARK_ARCHIVE = '{}/workflows/{}/downloads/archive'
BENCHMARK_FILE = '{}/workflows/{}/downloads/files/{}'
BENCHMARK_GET = '{}/workflows/{}'
BENCHMARK_LEADERBOARD = '{}/workflows/{}/leaderboard'
RUN_ARCHIVE = '{}/runs/{}/downloads/archive'
RUN_FILE = '{}/runs/{}/downloads/files/{}'
RUN_GET = '{}/runs/{}'
RUN_CANCEL = RUN_GET
RUN_DELETE = RUN_GET
RUNS_LIST = '{}/groups/{}/runs'
SUBMISSION_CREATE = '{}/workflows/{}/groups'
SUBMISSION_FILES = '{}/uploads/{}/files'
SUBMISSION_FILE = '{}/uploads/{}/files/{}'
SUBMISSION_RUN = '{}/groups/{}/runs'


@pytest.fixture
def prepare_submission(client, benchmark_id):
    """Prepare submission and return the client, user token (header), the
    benahcmark identifier , submission identifier and uploaded file identifier.
    """
    _, token = create_user(client, '0000')
    headers = {HEADER_TOKEN: token}
    url = SUBMISSION_CREATE.format(config.API_PATH(), benchmark_id)
    r = client.post(url, json={glbls.GROUP_NAME: 'S1'}, headers=headers)
    submission_id = r.json[glbls.GROUP_ID]
    data = {'file': (io.BytesIO(b'Alice\nBob'), 'names.txt')}
    url = SUBMISSION_FILES.format(config.API_PATH(), submission_id)
    r = client.post(url, data=data, content_type='multipart/form-data', headers=headers)
    file_id = r.json[flbls.FILE_ID]
    return client, headers, benchmark_id, submission_id, file_id


def test_cancel_run(prepare_submission):
    """Test cancelling a submission run."""
    # Create user, submission and upload the run file.
    client, headers, benchmark_id, submission_id, file_id = prepare_submission
    # -- Start run ------------------------------------------------------------
    url = SUBMISSION_RUN.format(config.API_PATH(), submission_id)
    body = {
        rlbls.RUN_ARGUMENTS: [
            {'name': 'names', 'value': serialize_fh(file_id)},
            {'name': 'greeting', 'value': 'Hi'},
            {'name': 'sleeptime', 'value': 5}
        ]
    }
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 201
    run_id = r.json['id']
    # -- Cancel and delete run ------------------------------------------------
    url = RUN_CANCEL.format(config.API_PATH(), run_id)
    r = client.put(url, json={rlbls.CANCEL_REASON: 'Test'}, headers=headers)
    assert r.status_code == 200
    url = RUN_CANCEL.format(config.API_PATH(), run_id)
    # Error when cancelling inactive run or providing invalid body.
    r = client.put(url, headers=headers)
    assert r.status_code == 400
    r = client.put(url, json={'messgae': 'invalid'}, headers=headers)
    assert r.status_code == 400


def test_delete_run(prepare_submission):
    """Test deleting a submission run."""
    # Create user, submission and upload the run file.
    client, headers, benchmark_id, submission_id, file_id = prepare_submission
    # -- Start run ------------------------------------------------------------
    url = SUBMISSION_RUN.format(config.API_PATH(), submission_id)
    body = {
        rlbls.RUN_ARGUMENTS: [
            {'name': 'names', 'value': serialize_fh(file_id)},
            {'name': 'greeting', 'value': 'Hi'},
            {'name': 'sleeptime', 'value': 0}
        ]
    }
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 201
    run_id = r.json['id']
    url = RUN_GET.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    obj = r.json
    while obj['state'] == st.STATE_RUNNING:
        time.sleep(1)
        r = client.get(url, headers=headers)
        assert r.status_code == 200
        obj = r.json
    assert obj['state'] == st.STATE_SUCCESS
    # -- Delete run -----------------------------------------------------------
    url = RUNS_LIST.format(config.API_PATH(), submission_id)
    r = client.get(url, headers=headers)
    doc = r.json
    assert len(doc[rlbls.RUN_LIST]) == 1
    url = RUN_DELETE.format(config.API_PATH(), run_id)
    r = client.delete(url, headers=headers)
    assert r.status_code == 204
    url = RUNS_LIST.format(config.API_PATH(), submission_id)
    r = client.get(url, headers=headers)
    doc = r.json
    assert len(doc[rlbls.RUN_LIST]) == 0


def test_submission_run(prepare_submission):
    """Tests start and monitor a run and access run resources."""
    # Create user, submission and upload the run file.
    client, headers, benchmark_id, submission_id, file_id = prepare_submission
    # -- Start run ------------------------------------------------------------
    url = SUBMISSION_RUN.format(config.API_PATH(), submission_id)
    body = {
        rlbls.RUN_ARGUMENTS: [
            {'name': 'names', 'value': serialize_fh(file_id)},
            {'name': 'greeting', 'value': 'Hi'},
            {'name': 'sleeptime', 'value': 2}
        ]
    }
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 201
    run_id = r.json['id']
    # -- Monitor run state ----------------------------------------------------
    url = RUN_GET.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    obj = r.json
    while obj['state'] == st.STATE_RUNNING:
        time.sleep(1)
        r = client.get(url, headers=headers)
        assert r.status_code == 200
        obj = r.json
    assert obj['state'] == st.STATE_SUCCESS
    # -- Run resources --------------------------------------------------------
    resources = {r['name']: r for r in obj['files']}
    assert len(resources) == 2
    assert 'results/greetings.txt' in resources
    assert 'results/analytics.json' in resources
    result_file_id = resources['results/greetings.txt']['id']
    res_url = RUN_FILE.format(config.API_PATH(), run_id, result_file_id)
    r = client.get(res_url, headers=headers)
    assert r.status_code == 200
    data = str(r.data)
    assert 'Hi Alice' in data
    assert 'Hi Bob' in data
    # Run archive
    url = RUN_ARCHIVE.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    # -- Workflow resources ---------------------------------------------------
    url = BENCHMARK_GET.format(config.API_PATH(), benchmark_id)
    b = client.get(url).json
    counter = 0
    while 'postproc' not in b:
        counter += 1
        if counter == 10:
            break
        time.sleep(1)
        b = client.get(url).json
    assert counter < 10
    counter = 0
    while b['postproc']['state'] != st.STATE_SUCCESS:
        counter += 1
        if counter == 10:
            break
        time.sleep(1)
        b = client.get(url).json
    assert counter < 10
    url = BENCHMARK_ARCHIVE.format(config.API_PATH(), benchmark_id)
    r = client.get(url)
    assert r.status_code == 200
    assert 'results.tar.gz' in r.headers['Content-Disposition']
    resource_id = b['postproc']['files'][0]['id']
    url = BENCHMARK_FILE.format(config.API_PATH(), benchmark_id, resource_id)
    r = client.get(url)
    assert r.status_code == 200
    assert 'results/compare.json' in r.headers['Content-Disposition']
    # -- Leaderboard ----------------------------------------------------------
    url = BENCHMARK_LEADERBOARD.format(config.API_PATH(), benchmark_id)
    r = client.get(url)
    assert r.status_code == 200
    url += '?includeAll'
    r = client.get(url)
    assert r.status_code == 200
    url += '=true'
    r = client.get(url)
    assert r.status_code == 200
    url += '&orderBy=max_len:asc,max_line:desc,avg_count'
    r = client.get(url)
    assert r.status_code == 200
    # Error for runs with invalid arguments.
    url = SUBMISSION_RUN.format(config.API_PATH(), submission_id)
    body = {
        rlbls.RUN_ARGUMENTS: [
            {'name': 'names', 'value': serialize_fh(file_id)},
            {'name': 'greeting', 'value': 'Hi'},
            {'name': 'sleepfor', 'value': 2}
        ]
    }
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 400
