# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests that create, retrieve, and authenticate users."""

import json

import flowserv.config.api as config
import flowserv.tests.serialize as serialize
import robflask.api.user as user
import robflask.api.util as util
import robflask.service as service


LABELS = {
    'ID': user.LABEL_ID,
    'NAME': user.LABEL_NAME,
    'PASSWORD': user.LABEL_PASSWORD,
    'REQUEST_ID': 'requestId',
    'TOKEN': 'token',
    'USERS': 'users',
    'VERIFY': user.LABEL_VERIFY_USER
}

USER = {
    LABELS['NAME']: 'user1',
    LABELS['PASSWORD']: 'pwd',
    LABELS['VERIFY']: True
}


def test_list_users(client):
    """Test user listings."""
    # Create an inactive user
    r = client.post(config.API_PATH() + '/users/register', json=USER)
    user_id = json.loads(r.data)[LABELS['ID']]
    # The list of users is still empty. However, since the user is not logged
    # in we also cannot access the listing
    r = client.get(config.API_PATH() + '/users')
    assert r.status_code == 403
    # Activate and authenticate the user
    data = {LABELS['ID']: user_id}
    r = client.post(config.API_PATH() + '/users/activate', json=data)
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'pwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    token = json.loads(r.data)[LABELS['TOKEN']]
    headers = {util.HEADER_TOKEN: token}
    r = client.get(config.API_PATH() + '/users', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[LABELS['USERS']]) == 1
    # Create user that is active and get listing
    USER2 = {
        LABELS['NAME']: 'user2',
        LABELS['PASSWORD']: 'pwd',
        LABELS['VERIFY']: False
    }
    r = client.post(config.API_PATH() + '/users/register', json=USER2)
    assert r.status_code == 201
    r = client.get(config.API_PATH() + '/users', headers=headers)
    assert r.status_code == 200
    assert len(json.loads(r.data)[LABELS['USERS']]) == 2


def test_register_user(client):
    """Test creating and activating a user."""
    # Create an inactive user
    r = client.post(config.API_PATH() + '/users/register', json=USER)
    assert r.status_code == 201
    obj = json.loads(r.data)
    serialize.validate_user_handle(obj, False, inactive=True)
    user_id = obj[LABELS['ID']]
    user_name = obj[LABELS['NAME']]
    assert user_name == 'user1'
    # Ensure that the user cannot login until they have been activated
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'pwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    # Inactive users are unknown users
    assert r.status_code == 404
    # User can login after activation and the user list has one element
    data = {LABELS['ID']: user_id}
    r = client.post(config.API_PATH() + '/users/activate', json=data)
    assert r.status_code == 200
    serialize.validate_user_handle(json.loads(r.data), False, inactive=False)
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'pwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    assert r.status_code == 200
    serialize.validate_user_handle(json.loads(r.data), True, inactive=False)
    token = json.loads(r.data)[LABELS['TOKEN']]
    headers = {util.HEADER_TOKEN: token}
    # Whoami (user1)
    r = client.get(config.API_PATH() + '/users/whoami', headers=headers)
    assert r.status_code == 200
    obj = json.loads(r.data)
    serialize.validate_user_handle(obj, True, inactive=False)
    assert obj[LABELS['ID']] == user_id
    assert obj[LABELS['NAME']] == 'user1'
    assert obj[LABELS['TOKEN']] == token
    # Create a user with an existing user name will return a BAD REQUEST
    r = client.post(config.API_PATH() + '/users/register', json=USER)
    assert r.status_code == 400
    # Logout user without access token causes error
    r = client.post(config.API_PATH() + '/users/logout')
    assert r.status_code == 403
    # Logout user that is currently logged in
    r = client.post(config.API_PATH() + '/users/logout', headers=headers)
    assert r.status_code == 200
    # After logout the token is invalid (list and whaomi)
    r = client.get(config.API_PATH() + '/users', headers=headers)
    assert r.status_code == 403
    r = client.get(config.API_PATH() + '/users/whoami', headers=headers)
    assert r.status_code == 403


def test_reset_password(client):
    """Test password reset requests."""
    # Create user and login
    USER1 = dict(USER)
    USER1[LABELS['VERIFY']] = False
    r = client.post(config.API_PATH() + '/users/register', json=USER1)
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'pwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    token = json.loads(r.data)[LABELS['TOKEN']]
    headers = {util.HEADER_TOKEN: token}
    r = client.get(config.API_PATH() + '/users/whoami', headers=headers)
    assert r.status_code == 200
    # Reset password for user1. This should also invalidate the access token.
    data = {LABELS['NAME']: 'user1'}
    url = config.API_PATH() + '/users/password/request'
    r = client.post(url, json=data, headers=headers)
    assert r.status_code == 200
    req_id = json.loads(r.data)[LABELS['REQUEST_ID']]
    data = {LABELS['REQUEST_ID']: req_id, LABELS['PASSWORD']: 'passwd'}
    url = config.API_PATH() + '/users/password/reset'
    r = client.post(url, json=data, headers=headers)
    assert r.status_code == 200
    r = client.get(config.API_PATH() + '/users', headers=headers)
    assert r.status_code == 403
    # The old password is invalid
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'pwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    assert r.status_code == 404
    data = {LABELS['NAME']: 'user1', LABELS['PASSWORD']: 'passwd'}
    r = client.post(config.API_PATH() + '/users/login', json=data)
    assert r.status_code == 200
