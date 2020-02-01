# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Unit tests that start, query and delete runs via the Web API."""

import io
import json
import os


DIR = os.path.dirname(os.path.realpath(__file__))
NAMES_FILE = os.path.join(DIR, '../.files/data/names.txt')


def test_runs(client, benchmark, url_prefix):
    """Unit tests that start, query and delete runs."""
    # Create common request header that contains the API key
    user_1, token_1 = create_user(client, url_prefix)
    headers = {service.HEADER_TOKEN: token_1}
    _, token_2 = create_user(client, url_prefix)
    # Create a new submission.
    benchmark_id = benchmark.identifier
    url = '{}/benchmarks/{}/submissions'.format(url_prefix, benchmark_id)
    r = client.post(url, json={labels.NAME: 'Submission'}, headers=headers)
    assert r.status_code == 201
    submission_id = json.loads(r.data)[labels.ID]
    # Upload a new file
    data = dict()
    with open(NAMES_FILE, 'rb') as f:
        data['file'] = (io.BytesIO(f.read()), 'names.txt')
    url = '{}/submissions/{}/files'.format(url_prefix, submission_id)
    r = client.post(
        url,
        data=data,
        content_type='multipart/form-data',
        headers=headers
    )
    assert r.status_code == 201
    file_id = json.loads(r.data)[labels.ID]
    # Start a new run
    url = '{}/submissions/{}/runs'.format(url_prefix, submission_id)
    body = {
        labels.ARGUMENTS: [
            {
                labels.ID: 'names',
                labels.VALUE: file_id
            },
            {
                labels.ID: 'greeting',
                labels.VALUE: 'Hi'
            }
        ]
    }
    r = client.post(url, json=body, headers=headers)
    assert r.status_code == 201
    run_id = json.loads(r.data)[labels.ID]
    # Get the run handle
    url = '{}/runs/{}'.format(url_prefix, run_id)
    r = client.get(url, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 403
    r = client.get(url, headers=headers)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert obj[labels.STATE] == state.STATE_SUCCESS
    resources = {r[labels.NAME]: r for r in obj[labels.RESOURCES]}
    assert len(resources) == 2
    assert 'results/greetings.txt' in resources
    assert 'results/analytics.json' in resources
    res_id = resources['results/greetings.txt'][labels.ID]
    res_url = '{}/runs/{}/downloads/resources/{}'.format(
        url_prefix,
        run_id,
        res_id
    )
    r = client.get(res_url, headers=headers)
    assert r.status_code == 200
    data = str(r.data)
    assert 'Hi Alice' in data
    assert 'Hi Bob' in data
    # Forbidden access to a resource
    r = client.get(res_url, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 403
    # Unknown resource
    res_url = '{}/runs/{}/downloads/resources/{}'.format(
        url_prefix,
        run_id,
        'unknown'
    )
    r = client.get(res_url, headers=headers)
    assert r.status_code == 404
    # Delete the run
    url = '{}/runs/{}'.format(url_prefix, run_id)
    r = client.delete(url, headers={service.HEADER_TOKEN: token_2})
    assert r.status_code == 403
    r = client.delete(url, headers=headers)
    assert r.status_code == 204
    r = client.get(url, headers=headers)
    assert r.status_code == 404
