# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for submission runs and run results."""

from flask import Blueprint, jsonify, make_response, request, send_file

from robflask.service import jsonbody, service

import robcore.config.api as config
import robcore.util as util
import robcore.view.labels as labels
import robflask.error as err


bp = Blueprint('runs', __name__, url_prefix=config.API_PATH())


@bp.route('/submissions/<string:submission_id>/runs', methods=['GET'])
def list_runs(submission_id):
    """Get a listing of all runs for a given submission. The user has to be a
    submission member in order to be authorized to list the runs.

    Parameters
    ----------
    submission_id: string
        Unique submission identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().list_runs(
            submission_id=submission_id,
            user=api.authenticate(request)
        )
    return make_response(jsonify(r), 200)


@bp.route('/submissions/<string:submission_id>/runs', methods=['POST'])
def start_run(submission_id):
    """Start a new run. Expects argument values for each mandatory benchmark
    parameter in the request body. The user has to be a submission member in
    order to be authorized to start new submission runs.

    Parameters
    ----------
    submission_id: string
        Unique submission identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    # Verify that the request contains a valid Json object that contains a
    # optional list of workflow arguments.
    obj = jsonbody(request, optional_labels=[labels.ARGUMENTS])
    args = obj[labels.ARGUMENTS] if labels.ARGUMENTS in obj else dict()
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        try:
            r = api.runs().start_run(
                submission_id=submission_id,
                arguments=args,
                user=api.authenticate(request)
            )
        except err.UnknownParameterError as ex:
            # Convert unknown parameter errors into invalid request errors
            # to avoid sending a 404 response
            raise err.InvalidRequest(str(ex))
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
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().get_run(
            run_id=run_id,
            user=api.authenticate(request)
        )
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
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        api.runs().delete_run(
            run_id=run_id,
            user=api.authenticate(request)
        )
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
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    # If the body contains a Json object verify that the object has the
    # mandatory element 'reason'
    reason = None
    if request.json:
        try:
            obj = util.validate_doc(
                request.json,
                mandatory_labels=[labels.REASON]
            )
            reason = obj[labels.REASON]
        except ValueError as ex:
            raise err.InvalidRequest(str(ex))
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.runs().cancel_run(
            run_id=run_id,
            user=api.authenticate(request),
            reason=reason
        )
    return make_response(jsonify(r), 200)


@bp.route('/runs/<string:run_id>/resources/<string:resource_id>')
def download_resource_file(run_id, resource_id):
    """Download a resource file that was generated by a successful workflow run.
    The user has to be a member of the submission in order to be allowed to
    access files.

    Parameters
    ----------
    run_id: string
        Unique run identifier
    resource_id: string
        Unique resource file identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    robflask.error.UnauthorizedAccessError
    robflask.error.UnknownObjectError
    """
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        fh = api.runs().get_resource_file(
            run_id=run_id,
            resource_id=resource_id,
            user=api.authenticate(request)
        )
    return send_file(
        fh.filepath,
        as_attachment=True,
        attachment_filename=fh.file_name,
        mimetype=fh.mimetype
    )
