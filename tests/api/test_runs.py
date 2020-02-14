# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Unit tests that start, query and delete runs via the Web API."""

import json
import os
import time

from robflask.tests.submission import create_submission, upload_file

import flowserv.config.api as config
import flowserv.model.workflow.state as st
import robflask.tests.serialize as serialize


DIR = os.path.dirname(os.path.realpath(__file__))
NAMES_FILE = os.path.join(DIR, '../.files/data/names.txt')


def test_runs(client):
    """Unit tests that start, query and delete runs."""
    # Create user and submission.
    s_id, headers_1, headers_2 = create_submission(client)
    # Upload a new file
    file_id = upload_file(client, s_id, headers_1, NAMES_FILE)
    # -- Start run ------------------------------------------------------------
    url = '{}/submissions/{}/runs'.format(config.API_PATH(), s_id)
    body = {
        'arguments': [
            {'id': 'names', 'value': file_id},
            {'id': 'greeting', 'value': 'Hi'}
        ]
    }
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 201
    run_id = json.loads(r.data)['id']
    # -- Monitor run state ----------------------------------------------------
    url = '{}/runs/{}'.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    obj = json.loads(r.data)
    while obj['state'] == st.STATE_RUNNING:
        time.sleep(1)
        r = client.get(url, headers=headers_1)
        assert r.status_code == 200
        obj = json.loads(r.data)
        serialize.validate_run_handle(obj, state=obj['state'])
    assert obj['state'] == st.STATE_SUCCESS
    serialize.validate_run_handle(obj, state=st.STATE_SUCCESS)
    benchmark_id = obj['benchmark']
    # -- Run resources --------------------------------------------------------
    resources = {r['name']: r for r in obj['resources']}
    assert len(resources) == 2
    assert 'results/greetings.txt' in resources
    assert 'results/analytics.json' in resources
    res_id = resources['results/greetings.txt']['id']
    res_url = '{}/runs/{}/downloads/resources/{}'.format(
        config.API_PATH(),
        run_id,
        res_id
    )
    r = client.get(res_url, headers=headers_1)
    assert r.status_code == 200
    data = str(r.data)
    assert 'Hi Alice' in data
    assert 'Hi Bob' in data
    # Run archive
    url = '{}/runs/{}/downloads/archive'.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    # -- Workflow resources ---------------------------------------------------
    url = '{}/benchmarks/{}'.format(config.API_PATH(), benchmark_id)
    b = json.loads(client.get(url).data)
    serialize.validate_benchmark_handle(b)
    counter = 0
    while 'postproc' not in b:
        counter += 1
        if counter == 10:
            break
        time.sleep(1)
        b = json.loads(client.get(url).data)
    assert counter < 10
    counter = 0
    while b['postproc']['state'] != st.STATE_SUCCESS:
        counter += 1
        if counter == 10:
            break
        time.sleep(1)
        b = json.loads(client.get(url).data)
    assert counter < 10
    url = '{}/benchmarks/{}/downloads/archive'
    url = url.format(config.API_PATH(), benchmark_id)
    r = client.get(url)
    assert r.status_code == 200
    assert 'results.tar.gz' in r.headers['Content-Disposition']
    url = '{}/benchmarks/{}/downloads/resources/{}'
    resource_id = b['postproc']['resources'][0]['id']
    url = url.format(config.API_PATH(), benchmark_id, resource_id)
    r = client.get(url)
    assert r.status_code == 200
    assert 'results/compare.json' in r.headers['Content-Disposition']
    # -- Cancel run -----------------------------------------------------------
    url = '{}/submissions/{}/runs'.format(config.API_PATH(), s_id)
    r = client.post(url, json=body, headers=headers_1)
    assert r.status_code == 201
    run_id = json.loads(r.data)['id']
    url = '{}/runs/{}'.format(config.API_PATH(), run_id)
    r = client.get(url, headers=headers_1)
    obj = json.loads(r.data)
    assert obj['state'] == st.STATE_RUNNING
    r = client.put(url, json={'reason': 'no need'}, headers=headers_1)
    r = client.get(url, headers=headers_1)
    obj = json.loads(r.data)
    assert obj['state'] == st.STATE_CANCELED
    assert obj['messages'][0] == 'no need'
    # -- List runs ------------------------------------------------------------
    url = '{}/submissions/{}/runs'.format(config.API_PATH(), s_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert len(obj['runs']) == 2
    # -- Poll runs ------------------------------------------------------------
    url = '{}/submissions/{}/runs/poll'.format(config.API_PATH(), s_id)
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert len(obj['runs']) == 0
    url = '{}/submissions/{}/runs/poll?state={}'.format(
        config.API_PATH(),
        s_id,
        st.STATE_CANCELED
    )
    r = client.get(url, headers=headers_1)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert len(obj['runs']) == 1
    # -- Error cases ----------------------------------------------------------
    # Forbidden access to run or resource
    r = client.get(url, headers=headers_2)
    assert r.status_code == 403
    # The access to run resources is open to all
    r = client.get(res_url, headers=headers_2)
    assert r.status_code == 200
    # Unknown resource
    res_url = '{}/runs/{}/downloads/resources/{}'.format(
        config.API_PATH(),
        run_id,
        'unknown'
    )
    r = client.get(res_url, headers=headers_1)
    assert r.status_code == 404
    # Delete the run
    url = '{}/runs/{}'.format(config.API_PATH(), run_id)
    r = client.delete(url, headers=headers_2)
    assert r.status_code == 403
    r = client.delete(url, headers=headers_1)
    assert r.status_code == 204
    r = client.get(url, headers=headers_1)
    assert r.status_code == 404
    # -- Submission handle contains runs --------------------------------------
    url = '{}/submissions/{}'.format(config.API_PATH(), s_id)
    r = client.get(url, headers=headers_1)
    obj = json.loads(r.data)
    assert len(obj['runs']) > 0
    print(json.dumps(obj, indent=4))
    serialize.validate_submission_handle(obj)
    # -- Ranking --------------------------------------------------------------
    # Start by adding a new run
    url = '{}/submissions/{}/runs'.format(config.API_PATH(), s_id)
    body = {
        'arguments': [
            {'id': 'names', 'value': file_id},
            {'id': 'greeting', 'value': 'Hi'}
        ]
    }
    r = client.post(url, json=body, headers=headers_1)
    run_id = json.loads(r.data)['id']
    url = '{}/runs/{}'.format(config.API_PATH(), run_id)
    obj = json.loads(r.data)
    while obj['state'] == st.STATE_RUNNING:
        time.sleep(1)
        r = client.get(url, headers=headers_1)
        obj = json.loads(r.data)
    url = '{}/benchmarks/{}/leaderboard'
    url = url.format(config.API_PATH(), benchmark_id)
    r = client.get(url)
    assert r.status_code == 200
    obj = json.loads(r.data)
    serialize.validate_ranking(obj)
    assert len(obj['ranking']) == 1
    url = url + '?orderBy=avg_count,max_len:asc,max_line:desc&includeAll'
    r = client.get(url)
    assert r.status_code == 200
    obj = json.loads(r.data)
    serialize.validate_ranking(obj)
    assert len(obj['ranking']) == 2
