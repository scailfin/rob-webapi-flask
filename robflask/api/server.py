# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for the service descriptor."""

from flask import Blueprint, jsonify, request

from robflask.api.auth import ACCESS_TOKEN

import flowserv.config.api as config


bp = Blueprint('service', __name__, url_prefix=config.API_PATH())


# List of currently supported routes
ROUTES = [
    'home=',
    'benchmarks:list=benchmarks',
    'benchmarks:get=benchmarks/{benchmarkId}',
    'benchmarks:ranking=benchmarks/{benchmarkId}/leaderboard',
    'benchmarks:archive=benchmarks/{benchmarkId}/downloads/archive',
    'benchmarks:resource=benchmarks/{benchmarkId}/downloads/resources/{resourceId}',  # noqa: E501
    'benchmarks:submissions=benchmarks/{benchmarkId}/submissions',
    'submissions:create=benchmarks/{benchmarkId}/submissions',
    'submissions:list=submissions',
    'submissions:delete=submissions/{submissionId}',
    'submissions:get=submissions/{submissionId}',
    'submissions:update=submissions/{submissionId}',
    'submissions:runs=submissions/{submissionId}/runs',
    'submissions:submit=submissions/{submissionId}/runs',
    'runs:delete=runs/{runId}',
    'runs:get=runs/{runId}',
    'runs:cancel=runs/{runId}',
    'runs:poll=submissions/{submissionId}/runs/poll',
    'runs:archive=runs/{runId}/downloads/archive',
    'runs:resource=runs/{runId}/downloads/resources/{resourceId}',
    'uploads:list=submissions/{submissionId}/files',
    'uploads:upload=submissions/{submissionId}/files',
    'uploads:delete=submissions/{submissionId}/files/{fileId}',
    'uploads:download=submissions/{submissionId}/files/{fileId}',
    'users:list=users',
    'users:activate=users/activate',
    'users:login=users/login',
    'users:logout=users/logout',
    'users:requestReset=users/password/request',
    'users:reset=users/password/reset',
    'users:register=users/register',
    'users:whoami=users/whoami'
]


@bp.route('/', methods=['GET'])
def service_descriptor():
    """Get the API service descriptor."""
    # If the request contains an access token we validate that the token is
    # still active
    from robflask.service.base import service
    with service() as api:
        # The access token is optional for the service descriptor. Make sure
        # not to raise an error if no token is present.
        token = ACCESS_TOKEN(request, raise_error=False)
        # Get the default descriptor and add route information
        baseurl = config.API_URL()
        routes = list()
        for route in ROUTES:
            rel, href = route.split('=')
            pattern = '{}/{}'.format(baseurl, href)
            routes.append({'action': rel, 'pattern': pattern})
        doc = api.service_descriptor(token)
        doc['routes'] = routes
        return jsonify(doc), 200
