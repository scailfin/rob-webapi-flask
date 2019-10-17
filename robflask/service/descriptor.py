# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for the service descriptor."""

from flask import Blueprint, jsonify

from robcore.api.service.server import Service

import robcore.config.api as config


bp = Blueprint('service', __name__, url_prefix=config.API_PATH())

@bp.route('/', methods=['GET'])
def service_descriptor():
    """Get the API service descriptor."""
    return jsonify(Service().service_descriptor()), 200
