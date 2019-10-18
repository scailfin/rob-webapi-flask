# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for user authentication and the user manager service."""

from flask import Blueprint, jsonify, make_response, request

from robflask.service import jsonbody, service

import robcore.api.serialize.labels as labels
import robcore.config.api as config


bp = Blueprint('users', __name__, url_prefix=config.API_PATH())


@bp.route('/users', methods=['GET'])
def list_users():
    """Get listing of registered users. Only users that are registered and
    currently logged in are allowed to query the database.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    """
    query = request.args.get('query')
    with service() as api:
        # Authenticate the user from expected the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        api.authenticate(request)
        r = api.users().list_users(query=query)
    return make_response(jsonify(r), 200)


@bp.route('/users/activate', methods=['POST'])
def activate_user():
    """Activate a newly registered user based on their unique user identifier.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object and get the user
    # identifier
    obj = jsonbody(request, mandatory_labels=[labels.ID])
    user_id = obj[labels.ID]
    # Activate user in the database and return the serialized user handle
    with service() as api:
        r = api.users().activate_user(user_id=user_id)
    return make_response(jsonify(r), 200)


@bp.route('/users/login', methods=['POST'])
def login_user():
    """Authenticate a user based on the given credentials. Returns the api_key
    that the user will use in subsequent requests.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object
    obj = jsonbody(request, mandatory_labels=[labels.USERNAME, labels.PASSWORD])
    # Get the name and password for the new user
    user = obj[labels.USERNAME]
    passwd = obj[labels.PASSWORD]
    # Register user in the database and return the serialized user handle
    with service() as api:
        r = api.users().login_user(username=user, password=passwd)
    return make_response(jsonify(r), 200)


@bp.route('/users/logout', methods=['POST'])
def logout_user():
    """Logout user. Expects an api_key for the authenticated user that is being
    logged out.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    """
    with service() as api:
        # Get handle for authenticated user. This will raise an error if the
        # user is currently not logged in.
        user = api.authenticate(request)
        # Logout user
        r = api.users().logout_user(user=user)
    return make_response(jsonify(r), 200)


@bp.route('/users/register', methods=['POST'])
def register_user():
    """Create a new user. Raises an InvalidRequest object if the request does
    not contain a JSON object with a user name and password for the new user.

    If the request body contains the optional verify flag and if the flag is
    set to False, the user will be activated immediately.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object
    obj = jsonbody(
        request,
        mandatory_labels=[labels.USERNAME, labels.PASSWORD],
        optional_labels=[labels.VERIFY_USER]
    )
    # Get the name and password for the new user and the value of the verify
    # flag. By default the flag is set to True
    user = obj[labels.USERNAME]
    passwd = obj[labels.PASSWORD]
    if labels.VERIFY_USER in obj:
        verify = bool(obj[labels.VERIFY_USER])
    else:
        verify = True
    # Register user in the database and return the serialized user handle
    with service() as api:
        r = api.users().register_user(
            username=user,
            password=passwd,
            verify=verify
        )
    return make_response(jsonify(r), 201)


@bp.route('/users/password/request', methods=['POST'])
def request_password_reset():
    """Request to rest the passowrd for a given user.

    Returns
    -------
    flask.response_class
    """
    # Verify that the request contains a valid Json object and get the name of
    # the user whose password is being rest.
    obj = jsonbody(request, mandatory_labels=[labels.USERNAME])
    user = obj[labels.USERNAME]
    # Register user in the database and return the serialized user handle
    with service() as api:
        r = api.users().request_password_reset(username=user)
    return make_response(jsonify(r), 200)


@bp.route('/users/password/reset', methods=['POST'])
def reset_password():
    """Reset the passowrd for a user. The user is identified by the request
    identifier in the request body. This identifier is expected to have been
    generated by a preceeding reset request.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.ConstraintViolationError
    """
    # Verify that the request contains a valid Json object
    mandatory_labels = [labels.REQUEST_ID, labels.PASSWORD]
    obj = jsonbody(request, mandatory_labels=mandatory_labels)
    # Get the unique request identifier and the new user password
    req_id = obj[labels.REQUEST_ID]
    passwd = obj[labels.PASSWORD]
    # Reset the password for the user that is identified by the request id
    with service() as api:
        r = api.users().reset_password(request_id=req_id, password=passwd)
    return make_response(jsonify(r), 200)


@bp.route('/users/whoami', methods=['GET'])
def whoami_user():
    """Get information about user that is associated with the provided access
    token.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    """
    # Return serialization of handle for user that is associated with the
    # api_key in the request header
    with service() as api:
        r = api.users().whoami_user(api.authenticate(request))
    return make_response(jsonify(r), 200)
