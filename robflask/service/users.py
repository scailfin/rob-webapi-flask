# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for user authentication and the user manager service."""

from flask import Blueprint, jsonify, make_response, request

from robcore.api.service.user import UserService
from robcore.db.driver import DatabaseDriver
from robcore.model.user.base import UserManager
from robcore.model.user.auth import DefaultAuthPolicy

import robcore.api.serialize.labels as labels
import robcore.config.api as config
import robcore.util as util
import robflask.error as err


bp = Blueprint('users', __name__, url_prefix=config.API_PATH())


@bp.route('/users', methods=['GET'])
def list_users():
    """Get listing of registered users."""
    query = request.args.get('query')
    with Service() as users:
        response = users.list_users(query=query)
    return make_response(jsonify(response), 200)


@bp.route('/users/register', methods=['POST'])
def register_user():
    """Create a new user. Raises an InvalidRequest object if the request does
    not contain a JSON object with a user name and password for the new user.

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object
    if not request.json:
        raise err.InvalidRequest('no JSON object')
    try:
        obj = util.validate_doc(
            request.json,
            mandatory_labels=[labels.USERNAME, labels.PASSWORD]
        )
    except ValueError as ex:
        raise err.InvalidRequest(str(ex))
    # Get the name and password for the new user
    username = obj[labels.USERNAME]
    password = obj[labels.PASSWORD]
    # Register user in the database and return the serialized user handle
    with Service() as users:
        response = users.register_user(username=username, password=password)
    return make_response(jsonify(response), 201)


# -- Helper class to instantiate and close the user service --------------------

class Service(object):
    """The local service object is a context manager for an instance of the user
    service class for the ROB API. The context manager maintains an open
    database connection and ensures that the connection is closed when the
    guard exit method is called.
    """
    def __init__(self):
        """Open a connection to the underlying database."""
        self.con = DatabaseDriver.get_connector().connect()

    def __enter__(self):
        """The enter method of the service guard returns a new instance of the
        user service.

        Returns
        -------
        robcore.model.user.base.UserManager
        """
        return UserService(
            manager=UserManager(con=self.con),
            auth=DefaultAuthPolicy(con=self.con)
        )

    def __exit__(self, type, value, traceback):
        """Close the database connection. Always returns False to ensure that
        potential exception are re-raised.

        Returns
        -------
        bool
        """
        self.con.close()
        # Ensure that exceptions are re-raised
        return False
