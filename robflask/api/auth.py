# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for handling web server requests."""

from flowserv.error import UnauthenticatedAccessError
from flowserv.service.api import HEADER_TOKEN


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
