# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for handling web server requests."""

from typing import Dict

from flowserv.error import UnauthenticatedAccessError
from flowserv.service.remote import HEADER_TOKEN
from flowserv.util import validate_doc

import robflask.error as err


def ACCESS_TOKEN(request, raise_error=True) -> str:
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


def jsonbody(request, mandatory=None, optional=None) -> Dict:
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
    try:
        return validate_doc(
            request.json,
            mandatory=mandatory,
            optional=optional
        )
    except (AttributeError, TypeError, ValueError) as ex:
        raise err.InvalidRequestError(str(ex))
