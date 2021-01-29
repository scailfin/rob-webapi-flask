# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for benchmark resources and benchmark leader boards."""

from flask import Blueprint, jsonify, make_response, request, send_file

from flowserv.model.template.schema import SortColumn
from robflask.api.util import ACCESS_TOKEN

import robflask.config as config


bp = Blueprint('workflows', __name__, url_prefix=config.API_PATH())


@bp.route('/workflows', methods=['GET'])
def list_benchmarks():
    """Get listing of available benchmarks. The benchmark listing is available
    to everyone, independent of whether they are currently authenticated or
    not.
    """
    from robflask.service import service
    with service() as api:
        r = api.workflows().list_workflows()
    return make_response(jsonify(r), 200)


@bp.route('/workflows/<string:workflow_id>', methods=['GET'])
def get_benchmark(workflow_id):
    """Get handle for given a benchmark. Benchmarks are available to everyone,
    independent of whether they are currently authenticated or not.
    """
    # Get the access token first. Do not raise raise an error if no token is
    # present.
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request, raise_error=False)) as api:
        r = api.workflows().get_workflow(workflow_id=workflow_id)
    return make_response(jsonify(r), 200)


@bp.route('/workflows/<string:workflow_id>/leaderboard', methods=['GET'])
def get_leaderboard(workflow_id):
    """Get leader board for a given benchmark. Benchmarks and their results are
    available to everyone, independent of whether they are authenticated or
    not.
    """
    # The orderBy argument can include a list of column names. Each column name
    # may be suffixed by the sort order.
    order_by = request.args.get('orderBy')
    if order_by is not None:
        sort_columns = list()
        for col in order_by.split(','):
            sort_desc = None
            pos = col.find(':')
            if pos > -1:
                if col[pos + 1:].lower() == 'asc':
                    sort_desc = False
                col = col[:pos]
            sort_columns.append(SortColumn(col, sort_desc=sort_desc))
    else:
        sort_columns = None
    # The includeAll argument is a flag. If the argument is given without value
    # the default is True. Otherwise, we expect a string that is equal to true.
    include_all = request.args.get('includeAll')
    if include_all is not None:
        if include_all == '':
            include_all = True
        else:
            include_all = include_all.lower() == 'true'
    # Get serialization of the result ranking
    from robflask.service import service
    with service() as api:
        r = api.workflows().get_ranking(
            workflow_id,
            order_by=sort_columns,
            include_all=include_all
        )
    return make_response(jsonify(r), 200)


@bp.route('/workflows/<string:workflow_id>/downloads/archive')
def download_benchmark_archive(workflow_id):
    """Download a compressed tar archive containing all current resource files
    for a benchmark that were created during post-processing.
    """
    from robflask.service import service
    with service() as api:
        fh = api.workflows().get_result_archive(workflow_id)
    return send_file(
        fh.open(),
        as_attachment=True,
        attachment_filename='results.tar.gz',
        mimetype='application/gzip'
    )


@bp.route('/workflows/<string:workflow_id>/downloads/files/<string:file_id>')
def get_benchmark_resource(workflow_id, file_id):
    """Download the current resource file for a benchmark resource that was
    created during post-processing.
    """
    from robflask.service import service
    with service() as api:
        fh = api.workflows().get_result_file(
            workflow_id=workflow_id,
            file_id=file_id
        )
        attachment_filename = fh.name
        mimetype = fh.mime_type
    return send_file(
        fh.open(),
        as_attachment=True,
        attachment_filename=attachment_filename,
        mimetype=mimetype
    )
