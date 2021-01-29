# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for the service descriptor."""

from flask import Blueprint, jsonify, request

from robflask.api.util import ACCESS_TOKEN

import robflask.config as config


bp = Blueprint('service', __name__, url_prefix=config.API_PATH())


@bp.route('/', methods=['GET'])
def service_descriptor():
    """Get the API service descriptor."""
    # If the request contains an access token we validate that the token is
    # still active. The access token is optional for the service descriptor.
    # Make sure not to raise an error if no token is present.
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request, raise_error=False)) as api:
        return jsonify(api.server().to_dict()), 200
