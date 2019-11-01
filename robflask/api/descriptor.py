# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for the service descriptor."""

from flask import Blueprint, jsonify, request

from robflask.service import service

import robcore.config.api as config
import robflask.error as err


bp = Blueprint('service', __name__, url_prefix=config.API_PATH())

@bp.route('/', methods=['GET'])
def service_descriptor():
    """Get the API service descriptor."""
    # If the request contains an access token we validate that the token is
    # still active
    with service() as api:
        return jsonify(api.service_descriptor(request)), 200
