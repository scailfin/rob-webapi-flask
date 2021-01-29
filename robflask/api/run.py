# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for submission runs and run results."""

from flask import Blueprint, jsonify, make_response, request, send_file

from flowserv.error import UnknownParameterError
from robflask.api.util import ACCESS_TOKEN, jsonbody

import flowserv.util as util
import flowserv.view.run as labels
import robflask.config as config
import robflask.error as err


bp = Blueprint('runs', __name__, url_prefix=config.API_PATH())


@bp.route('/groups/<string:group_id>/runs', methods=['GET'])
def list_runs(group_id):
    """Get a listing of all runs for a given submission. The user has to be a
    submission member in order to be authorized to list the runs.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().list_runs(group_id=group_id)
    return make_response(jsonify(r), 200)


@bp.route('/groups/<string:group_id>/runs', methods=['POST'])
def start_run(group_id):
    """Start a new run. Expects argument values for each mandatory benchmark
    parameter in the request body. The user has to be a submission member in
    order to be authorized to start new submission runs.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Verify that the request contains a valid Json object that contains a
    # optional list of workflow arguments.
    obj = jsonbody(request, optional=[labels.RUN_ARGUMENTS])
    args = obj[labels.RUN_ARGUMENTS] if labels.RUN_ARGUMENTS in obj else dict()
    from robflask.service import service
    with service(access_token=token) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        try:
            r = api.runs().start_run(group_id=group_id, arguments=args)
        except UnknownParameterError as ex:
            # Convert unknown parameter errors into invalid request errors
            # to avoid sending a 404 response
            raise err.InvalidRequestError(str(ex))
    return make_response(jsonify(r), 201)


@bp.route('/runs/<string:run_id>', methods=['GET'])
def get_run(run_id):
    """Get handle for a given run. The user has to be a member of the run
    submission in order to be authorized to access the run.

    Parameters
    ----------
    run_id: string
        Unique run identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().get_run(run_id=run_id)
    return make_response(jsonify(r), 200)


@bp.route('/runs/<string:run_id>', methods=['DELETE'])
def delete_run(run_id):
    """Delete the run with the given identifier. The user has to be a member of
    the run submission in order to be authorized to delete the run.

    Parameters
    ----------
    run_id: string
        Unique run identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        api.runs().delete_run(run_id=run_id)
    return make_response(jsonify(dict()), 204)


@bp.route('/runs/<string:run_id>', methods=['PUT'])
def cancel_run(run_id):
    """Get handle for a given run. The user has to be a member of the run
    submission in order to be authorized to access the run.

    Parameters
    ----------
    run_id: string
        Unique run identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # If the body contains a Json object verify that the object has the
    # mandatory element 'reason'
    reason = None
    if request.json:
        try:
            obj = util.validate_doc(
                request.json,
                mandatory=['reason']
            )
            reason = obj['reason']
        except ValueError as ex:
            raise err.InvalidRequestError(str(ex))
    from robflask.service import service
    with service(access_token=token) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().cancel_run(
            run_id=run_id,
            reason=reason
        )
    return make_response(jsonify(r), 200)


@bp.route('/runs/<string:run_id>/downloads/archive')
def download_result_archive(run_id):
    """Download a compressed tar archive containing all result files that were
    generated by a given workflow run.

    NOTE: At this point, the user is not authenticated for file downloads to
    allow download in the GUI via browser redirect.

    Parameters
    ----------
    run_id: string
        Unique run identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnknownWorkflowGroupError
    """
    from robflask.service import service
    with service() as api:
        ioBuffer = api.runs().get_result_archive(run_id=run_id)
        return send_file(
            ioBuffer.open(),
            as_attachment=True,
            attachment_filename='run.tar.gz',
            mimetype='application/gzip'
        )


@bp.route('/runs/<string:run_id>/downloads/files/<string:file_id>')
def download_result_file(run_id, file_id):
    """Download a resource file that was generated by a successful workflow run.
    The user has to be a member of the submission in order to be allowed to
    access files.

    NOTE: At this point, the user is not authenticated for file downloads to
    allow download in the GUI via browser redirect.

    Parameters
    ----------
    run_id: string
        Unique run identifier
    file_id: string
        Unique resource file identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownWorkflowGroupError
    """
    print('download {} {}'.format(run_id, file_id))
    from robflask.service import service
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        fh = api.runs().get_result_file(run_id=run_id, file_id=file_id)
        return send_file(
            fh.open(),
            as_attachment=True,
            attachment_filename=fh.name,
            mimetype=fh.mime_type
        )
