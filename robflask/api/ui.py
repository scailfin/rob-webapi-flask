# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for serving the demo user interface."""

import os

from flask import Blueprint, send_from_directory

from robflask.config import ROB_UI_PATH


bp = Blueprint('robui', __name__, url_prefix='/rob-ui')


@bp.route('/<path:path>', methods=['GET'])
def send_ui_files(path):
    """Send static files for the ROB UI."""
    return send_from_directory(os.environ.get(ROB_UI_PATH), path)


@bp.route('/', methods=['GET'])
def send_ui_home():
    """Send index.html file for the ROB UI."""
    return send_from_directory(os.environ.get(ROB_UI_PATH), 'index.html')
