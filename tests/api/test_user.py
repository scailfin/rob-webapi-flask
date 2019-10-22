# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test app routes that create and authenticate users."""

import json

import robcore.view.labels as labels
import robflask.service as service


def test_users(client, url_prefix):
    """Unit tests that create and retrieve users. The function also tests the
    authentication functionality, and password resets.
    """
    # Create an inactive user and ensure that the user cannot login until
    # they have been activated
    body = {
        labels.USERNAME: 'user1',
        labels.PASSWORD: 'pwd',
        labels.VERIFY_USER: True
    }
    r = client.post(url_prefix + '/users/register', json=body)
    assert r.status_code == 201
    obj = json.loads(r.data)
    user_id = obj[labels.ID]
    user_name = obj[labels.USERNAME]
    assert user_name == 'user1'
    # Inactive users are unknown users
    login = {labels.USERNAME: 'user1', labels.PASSWORD: 'pwd'}
    r = client.post(url_prefix + '/users/login', json=login)
    assert r.status_code == 404
    # The list of users is still empty. However, since the user is not logged
    # in we also cannot access the listing
    r = client.get(url_prefix + '/users')
    assert r.status_code == 403
    # User can login after activation and the user list has one element
    r = client.post(url_prefix + '/users/activate', json={labels.ID: user_id})
    assert r.status_code == 200
    r = client.post(url_prefix + '/users/login', json=login)
    assert r.status_code == 200
    token = json.loads(r.data)[labels.ACCESS_TOKEN]
    headers = {service.HEADER_TOKEN: token}
    r = client.get(url_prefix + '/users', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.USERS]) == 1
    # Whoami (user1)
    r = client.get(url_prefix + '/users/whoami', headers=headers)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert obj[labels.ID] == user_id
    assert obj[labels.USERNAME] == 'user1'
    assert obj[labels.ACCESS_TOKEN] == token
    # Create a user with an existing user name will return a BAD REQUEST
    r = client.post(url_prefix + '/users/register', json=body)
    assert r.status_code == 400
    # Create user that is active and get listing
    body = {
        labels.USERNAME: 'user2',
        labels.PASSWORD: 'pwd',
        labels.VERIFY_USER: False
    }
    r = client.post(url_prefix + '/users/register', json=body)
    assert r.status_code == 201
    r = client.get(url_prefix + '/users', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[labels.USERS]) == 2
    # Logout user (that is not logged in and that is logged in)
    r = client.post(url_prefix + '/users/logout')
    assert r.status_code == 403
    r = client.post(url_prefix + '/users/logout', headers=headers)
    assert r.status_code == 200
    # After logout the token is invalid (list and whaomi)
    r = client.get(url_prefix + '/users', headers=headers)
    assert r.status_code == 403
    r = client.get(url_prefix + '/users/whoami', headers=headers)
    assert r.status_code == 403
    # Login second user
    login = {labels.USERNAME: 'user2', labels.PASSWORD: 'pwd'}
    r = client.post(url_prefix + '/users/login', json=login)
    assert r.status_code == 200
    token = json.loads(r.data)[labels.ACCESS_TOKEN]
    headers = {service.HEADER_TOKEN: token}
    # Whoami (user2)
    r = client.get(url_prefix + '/users/whoami', headers=headers)
    assert r.status_code == 200
    obj = json.loads(r.data)
    assert obj[labels.ID] != user_id
    assert obj[labels.USERNAME] == 'user2'
    assert obj[labels.ACCESS_TOKEN] == token
    # Reset password for user2. This should also invalidate the access token
    request = {labels.USERNAME: 'user2'}
    r = client.post(url_prefix + '/users/password/request', json=request, headers=headers)
    assert r.status_code == 200
    req_id = json.loads(r.data)[labels.REQUEST_ID]
    reset = {labels.REQUEST_ID: req_id, labels.PASSWORD: 'passwd'}
    r = client.post(url_prefix + '/users/password/reset', json=reset, headers=headers)
    assert r.status_code == 200
    r = client.get(url_prefix + '/users', headers=headers)
    assert r.status_code == 403
    # The old password is invalid
    r = client.post(url_prefix + '/users/login', json=login)
    assert r.status_code == 404
    login[labels.PASSWORD] = 'passwd'
    r = client.post(url_prefix + '/users/login', json=login)
    assert r.status_code == 200
