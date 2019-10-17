# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper classes method to create instances of the API components. All
components use the same underlying database connection. The connection object
is under the control of of a context manager to ensure that the connection is
closed properly after every API request has been handled.
"""

from contextlib import contextmanager

from robcore.api.route import UrlFactory
from robcore.api.service.user import UserService
from robcore.db.driver import DatabaseDriver
from robcore.model.user.base import UserManager
from robcore.model.user.auth import DefaultAuthPolicy

import robcore.util as util
import robflask.error as err


class API(object):
    """The API object implements a factory pattern for all API components. The
    individual components are instantiated on-demand to avoid any overhead for
    components that are not required to handle a user request.
    """
    def __init__(self, con):
        """Initialize the database connection and the URL factory. The URL
        factory is kept as a class property since every API component will
        have an instance of this class.

        Parameters
        ----------
        con: DB-API 2.0 database connection
            Connection to underlying database
        """
        self.con = con
        self.urls = UrlFactory()
        # Keep a copy of the authentication object (only if created or requested
        # by one of the components that handle an API request).
        self._auth = None

    def auth(self):
        """Get authentication handler. The object is create only once.

        Returns
        -------
        robcore.model.user.auth.Auth
        """
        if self._auth is None:
            self._auth = DefaultAuthPolicy(con=self.con)
        return self._auth

    def authenticate(self, request):
        """Authenticate the user based on the api_key that is expected in the
        header of an API request. Returns the handle for the authenticated user.

        Parameters
        ----------
        request: flask.request
            Flask request object

        Returns
        -------
        robcore.model.user.base.UserHandle

        Raises
        ------
        robcore.error.UnauthenticatedAccessError
        """
        return self.auth().authenticate(request.headers.get('api_key'))

    def users(self):
        """Get an instance of the user service component.

        Returns
        -------
        robcore.api.service.user.UserService
        """
        return UserService(
            manager=UserManager(con=self.con),
            urls=self.urls
        )


# -- Helper methods for API request handling -----------------------------------

def jsonbody(request, mandatory_labels=None, optional_labels=None):
    """Get JSON object from the body of an API request. Validates the object
    based on the given (optional) lists of mandatory and optional labels.

    Returns the JSON object (dictionary). Raises an error if an invalid request
    or body is given.

    Parameters
    ----------
    request: flask.request
        HTTP request
    mandatory_labels: list(string)
        List of mandatory labels for the dictionary serialization
    optional_labels: list(string), optional
        List of optional labels for the dictionary serialization

    Returns
    -------
    dict

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
            mandatory_labels=mandatory_labels,
            optional_labels=optional_labels
        )
    except ValueError as ex:
        raise err.InvalidRequest(str(ex))
    return obj


@contextmanager
def service():
    """The local service function is a context manager for an open database
    connection that is used to instantiate the user service class for the ROB
    API. The context manager ensures that the database conneciton in closed
    after a API request has been processed.

    Returns
    -------
    robflask.service.API
    """
    con = DatabaseDriver.get_connector().connect()
    yield API(con)
    print('closing connection')
    con.close()
