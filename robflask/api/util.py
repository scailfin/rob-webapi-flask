# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for handling web server requests."""

from flowserv.core.error import UnauthenticatedAccessError
from flowserv.core.util import validate_doc

import robflask.error as err


"""Name of the header eleemnt that contains the access token."""
HEADER_TOKEN = 'api_key'


def ACCESS_TOKEN(request, raise_error=True):
    """Get the access token from the header of a given Flask request. Returns
    None if no token is present in the header and the raise error flag is
    False. Otherwise, an unauthenticated access error is raised.

    Parameters
    ----------
    request: flask.request
        Flask request object
    raise_error: bool, optional
        Raise error if no access token is present in the header

    Returns
    -------
    string

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    """
    token = request.headers.get(HEADER_TOKEN)
    if token is None and raise_error:
        raise UnauthenticatedAccessError()
    return token


def jsonbody(request, mandatory=None, optional=None):
    """Get Json object from the body of an API request. Validates the object
    based on the given (optional) lists of mandatory and optional labels.

    Returns the JSON object (dictionary). Raises an error if an invalid request
    or body is given.

    Parameters
    ----------
    request: flask.request
        HTTP request
    mandatory: list(string)
        List of mandatory labels for the dictionary serialization
    optional: list(string), optional
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
        return validate_doc(
            request.json,
            mandatory=mandatory,
            optional=optional
        )
    except ValueError as ex:
        raise err.InvalidRequest(str(ex))
