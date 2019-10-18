# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for benchmark resources and benchmark leader boards."""

from flask import Blueprint, jsonify, make_response, request

from robcore.model.template.schema import SortColumn
from robflask.service import jsonbody, service

import robcore.api.serialize.labels as labels
import robcore.config.api as config


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

        order_by: list(robcore.model.template.schema.SortColumn), optional
            Use the given attribute to sort run results. If not given the schema
            default attribute is used
        include_all: bool, optional
            Include at most one entry per submission in the result if False

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
