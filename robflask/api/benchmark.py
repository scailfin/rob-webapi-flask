# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for benchmark resources and benchmark leader boards."""

from flask import Blueprint, jsonify, make_response, request, send_file

from robcore.model.template.schema import SortColumn
from robflask.service import jsonbody, service

import robcore.config.api as config
import robcore.view.labels as labels


bp = Blueprint('benchmarks', __name__, url_prefix=config.API_PATH())


@bp.route('/benchmarks', methods=['GET'])
def list_benchmarks():
    """Get listing of available benchmarks. The benchmark listing is available
    to everyone, independent of whether they are currently authenticated or not.

    Returns
    -------
    flask.response_class
    """
    with service() as api:
        r = api.benchmarks().list_benchmarks()
    return make_response(jsonify(r), 200)


@bp.route('/benchmarks/<string:benchmark_id>', methods=['GET'])
def get_benchmark(benchmark_id):
    """Get handle for given a benchmark. Benchmarks are available to everyone,
    independent of whether they are currently authenticated or not.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnknownObjectError
    """
    with service() as api:
        r = api.benchmarks().get_benchmark(benchmark_id)
    return make_response(jsonify(r), 200)


@bp.route('/benchmarks/<string:benchmark_id>/leaderboard', methods=['GET'])
def get_leaderboard(benchmark_id):
    """Get leader board for a given benchmark. Benchmarks and their results are
    available to everyone, independent of whether they are authenticated or not.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier
    order_by: string, optional
        Comma-separated list of sore columns. Each column may be suffixed with
        the sort order. Use 'ASC' for ascending sort and any other value for
        descending sort.
    include_all: string, optional
        Boolean flag to indicate whether all results shoudl be included or at
        most one result per submission.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnknownObjectError
    """
    # The orderBy argument can include a list of column names. Each column name
    # may be suffixed by the sort order.
    order_by = request.args.get('orderBy')
    if not order_by is None:
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
    if include_all != None:
        if include_all == '':
            include_all = True
        else:
            include_all = include_all.lower() == 'true'
    # Get serialization of the result ranking
    with service() as api:
        r = api.benchmarks().get_leaderboard(
            benchmark_id,
            order_by=sort_columns,
            include_all=include_all
        )
    return make_response(jsonify(r), 200)


@bp.route('/benchmarks/<string:benchmark_id>/resources/<string:result_id>/<string:resource_id>', methods=['GET'])
def get_benchmark_resource(benchmark_id, result_id, resource_id):
    """Download the current resource file for a benchmark resource that was
    created during post-processing.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier
    result_id: string
        Unique identifier of the post-processing result set
    resource_id: string
        Unique resource identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnknownObjectError
    """
    with service() as api:
        bsrv = api.benchmarks()
        fh = bsrv.get_benchmark_resource(benchmark_id, result_id, resource_id)
    return send_file(
        fh.filepath,
        as_attachment=True,
        attachment_filename=fh.file_name
    )
