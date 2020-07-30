# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for user authentication and the user manager service."""

from flask import Blueprint, jsonify, make_response, request

from robflask.api.auth import ACCESS_TOKEN
from robflask.api.util import jsonbody

import flowserv.config.api as config


"""Labels for request bodys in POST and PUT requests."""
LABEL_ID = 'id'
LABEL_NAME = 'username'
LABEL_PASSWORD = 'password'
LABEL_REQUEST_ID = 'requestId'
LABEL_VERIFY_USER = 'verify'


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
    flowserv.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    from robflask.service.base import service
    with service() as api:
        # Authenticate the user from the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        api.authenticate(token)
        r = api.users().list_users(query=request.args.get('query'))
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
    obj = jsonbody(request, mandatory=[LABEL_ID])
    user_id = obj[LABEL_ID]
    # Activate user in the database and return the serialized user handle
    from robflask.service.base import service
    with service() as api:
        r = api.users().activate_user(user_id=user_id)
    return make_response(jsonify(r), 200)


@bp.route('/users/login', methods=['POST'])
def login_user():
    """Authenticate a user based on the given credentials. Returns the access
    token that the user will use in subsequent requests.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object
    obj = jsonbody(request, mandatory=[LABEL_NAME, LABEL_PASSWORD])
    # Get the name and password for the new user
    user = obj[LABEL_NAME]
    passwd = obj[LABEL_PASSWORD]
    # Register user in the database and return the serialized user handle
    from robflask.service.base import service
    with service() as api:
        r = api.users().login_user(username=user, password=passwd)
    return make_response(jsonify(r), 200)


@bp.route('/users/logout', methods=['POST'])
def logout_user():
    """Logout user. Expects an access token for the authenticated user that is
    being logged out.

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    from robflask.service.base import service
    with service() as api:
        # Logout user. Authentication will fail and raise an error if the
        # user is currently not logged in.
        r = api.users().logout_user(api_key=token)
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
        mandatory=[LABEL_NAME, LABEL_PASSWORD],
        optional=[LABEL_VERIFY_USER]
    )
    # Get the name and password for the new user and the value of the verify
    # flag. By default the flag is set to True
    user = obj[LABEL_NAME]
    passwd = obj[LABEL_PASSWORD]
    if LABEL_VERIFY_USER in obj:
        verify = bool(obj[LABEL_VERIFY_USER])
    else:
        verify = True
    # Register user in the database and return the serialized user handle
    from robflask.service.base import service
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
    obj = jsonbody(request, mandatory=[LABEL_NAME])
    user = obj[LABEL_NAME]
    # Register user in the database and return the serialized user handle
    from robflask.service.base import service
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
    mandatory_labels = [LABEL_REQUEST_ID, LABEL_PASSWORD]
    obj = jsonbody(request, mandatory=mandatory_labels)
    # Get the unique request identifier and the new user password
    req_id = obj[LABEL_REQUEST_ID]
    passwd = obj[LABEL_PASSWORD]
    # Reset the password for the user that is identified by the request id
    from robflask.service.base import service
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
    flowserv.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Return serialization of handle for user that is associated with access
    # token
    from robflask.service.base import service
    with service() as api:
        r = api.users().whoami_user(api_key=token)
    return make_response(jsonify(r), 200)
