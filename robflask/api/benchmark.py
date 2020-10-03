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
from robflask.api.auth import ACCESS_TOKEN

import flowserv.config.api as config


bp = Blueprint('benchmarks', __name__, url_prefix=config.API_PATH())


@bp.route('/benchmarks', methods=['GET'])
def list_benchmarks():
    """Get listing of available benchmarks. The benchmark listing is available
    to everyone, independent of whether they are currently authenticated or
    not.

    Returns
    -------
    flask.response_class
    """
    from robflask.service.base import service
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
    flowserv.error.UnknownWorkflowError
    """
    # Get the access token first. Do not raise raise an error if no token is
    # present.
    token = ACCESS_TOKEN(request, raise_error=False)
    from robflask.service.base import service
    with service() as api:
        # Set the user identifier depending on whether a token was given.
        if token is not None:
            user_id = api.authenticate(token).user_id
        else:
            user_id = None
        r = api.benchmarks().get_benchmark(
            benchmark_id=benchmark_id,
            user_id=user_id
        )
    return make_response(jsonify(r), 200)


@bp.route('/benchmarks/<string:benchmark_id>/leaderboard', methods=['GET'])
def get_leaderboard(benchmark_id):
    """Get leader board for a given benchmark. Benchmarks and their results are
    available to everyone, independent of whether they are authenticated or
    not.

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
    flowserv.error.UnknownWorkflowError
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
    from robflask.service.base import service
    with service() as api:
        r = api.benchmarks().get_leaderboard(
            benchmark_id,
            order_by=sort_columns,
            include_all=include_all
        )
    return make_response(jsonify(r), 200)


@bp.route('/benchmarks/<string:benchmark_id>/downloads/archive')
def download_benchmark_archive(benchmark_id):
    """Download a compressed tar archive containing all current resource files
    for a benchmark that were created during post-processing.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier

    Returns
    -------
    file

    Raises
    ------
    flowserv.error.UnknownWorkflowError
    flowserv.error.UnknownResourceError
    """
    from robflask.service.base import service
    with service() as api:
        ioBuffer = api.benchmarks().get_result_archive(benchmark_id)
    return send_file(
        ioBuffer,
        as_attachment=True,
        attachment_filename='results.tar.gz',
        mimetype='application/gzip'
    )


@bp.route(
    '/benchmarks/<string:benchmark_id>/downloads/resources/<string:file_id>'
)
def get_benchmark_resource(benchmark_id, file_id):
    """Download the current resource file for a benchmark resource that was
    created during post-processing.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier
    file_id: string
        Unique resource file identifier

    Returns
    -------
    file

    Raises
    ------
    flowserv.error.UnknownWorkflowError
    flowserv.error.UnknownResourceError
    """
    from robflask.service.base import service
    with service() as api:
        fh = api.benchmarks().get_result_file(
            benchmark_id=benchmark_id,
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
