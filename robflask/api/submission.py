# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for submission resources and file uploads."""

from flask import Blueprint, jsonify, make_response, request, send_file
from werkzeug.utils import secure_filename

from robflask.service import jsonbody, service

import robcore.api.serialize.labels as labels
import robcore.config.api as config
import robflask.error as err


bp = Blueprint('submissions', __name__, url_prefix=config.API_PATH())


@bp.route('/benchmarks/<string:benchmark_id>/submissions', methods=['POST'])
def create_submission(benchmark_id):
    """Create a new submission for a given benchmark. The user has to be
    authenticated in order to be able to create a new submission.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.InvalidRequest
    robflask.error.UnauthenticatedAccessError
    """
    # Verify that the request contains a valid Json object that contains the
    # submission name and an optional list of member identifier.
    obj = jsonbody(
        request,
        mandatory_labels=[labels.NAME],
        optional_labels=[labels.MEMBERS]
    )
    name = obj[labels.NAME]
    members = obj[labels.MEMBERS] if labels.MEMBERS in obj else None
    if not members is None and not isinstance(members, list):
        raise err.InvalidRequest('members not a list')
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        try:
            r = api.submissions().create_submission(
                benchmark_id=benchmark_id,
                name=name,
                user=api.authenticate(request),
                members=members
            )
        except err.UnknownUserError as ex:
            # Change error type from unknown object to invalid request if a
            # user in the member list is unknown
            raise err.InvalidRequest(str(ex))
    return make_response(jsonify(r), 201)


@bp.route('/benchmarks/<string:benchmark_id>/submissions', methods=['GET'])
def list_submission(benchmark_id):
    """Get a list of all submissions for a given benchmark. The user has to be
    authenticated in order to be able to access the submission list.

    Parameters
    ----------
    benchmark_id: string
        Unique benchmark identifier

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    """
    with service() as api:
        # Authenticate the user from the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        api.authenticate(request)
        r = api.submissions().list_submissions(benchmark_id=benchmark_id)
    return make_response(jsonify(r), 200)


@bp.route('/submissions', methods=['GET'])
def list_user_submission():
    """Get a list of all submissions that the authenticated user is a member of.

    Returns
    -------
    flask.response_class

    Raises
    ------
    robflask.error.UnauthenticatedAccessError
    """
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.submissions().list_submissions(user=api.authenticate(request))
    return make_response(jsonify(r), 200)


@bp.route('/submissions/<string:submission_id>', methods=['DELETE'])
def delete_submission(submission_id):
    """Delete the submission with the given identifier. The user has to be a
    submission member in order to be authorized to delete the submission.

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
        api.submissions().delete_submission(
            submission_id=submission_id,
            user=api.authenticate(request)
        )
    return make_response(jsonify(dict()), 204)


@bp.route('/submissions/<string:submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Get handle for the submission with the given identifier. The user has to
    be authenticated in order to access a submission.

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
    robflask.error.UnknownObjectError
    """
    with service() as api:
        # Authenticate the user from the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        api.authenticate(request)
        r = api.submissions().get_submission(submission_id=submission_id)
    return make_response(jsonify(r), 200)


@bp.route('/submissions/<string:submission_id>', methods=['PUT'])
def update_submission(submission_id):
    """Update the submission with the given identifier. The request body can
    contain a modified submission name and/or a modified list of submission
    members.

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
    # Verify that the request contains a valid Json object that contains an
    # optional submission name and/or a list of member identifier.
    obj = jsonbody(
        request,
        mandatory_labels=[],
        optional_labels=[labels.NAME, labels.MEMBERS]
    )
    name = obj[labels.NAME] if labels.NAME in obj else None
    members = obj[labels.MEMBERS] if labels.MEMBERS in obj else None
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.submissions().update_submission(
            submission_id=submission_id,
            user=api.authenticate(request),
            name=name,
            members=members
        )
    return make_response(jsonify(r), 200)


@bp.route('/submissions/<string:submission_id>/files', methods=['GET'])
def list_files(submission_id):
    """List all uploaded files fora given submission. The user has to be a
    member of the submission in order to be allowed to list files.

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
        r = api.submissions().list_files(
            submission_id=submission_id,
            user=api.authenticate(request)
        )
    return make_response(jsonify(r), 200)


@bp.route('/submissions/<string:submission_id>/files', methods=['POST'])
def upload_file(submission_id):
    """Upload a new file as part of a given submission. The user has to be a
    member of the submission in order to be allowed to upload files.

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
    # Ensure that the upload request contains a file object
    if request.files and 'file' in request.files:
        file = request.files['file']
        # A browser may submit a empty part without filename
        if file.filename == '':
            raise err.InvalidRequest('empty file name')
        # Save uploaded file to temp directory
        filename = secure_filename(file.filename)
        with service() as api:
            # Authentication of the user from the expected api_token in the header
            # will fail if no token is given or if the user is not logged in.
            r = api.submissions().upload_file(
                submission_id=submission_id,
                file=file,
                file_name=filename,
                user=api.authenticate(request)
            )
        return make_response(jsonify(r), 201)
    else:
        raise err.InvalidRequest('no file request')


@bp.route('/submissions/<string:submission_id>/files/<string:file_id>', methods=['GET'])
def download_file(submission_id, file_id):
    """Download a given file that was perviously uploaded for a submission. The
    user has to be a member of the submission in order to be allowed to access
    files.

    Parameters
    ----------
    submission_id: string
        Unique submission identifier
    file_id: string
        Unique file identifier

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
        fh, _ = api.submissions().get_file(
            submission_id=submission_id,
            file_id=file_id,
            user=api.authenticate(request)
        )
    return send_file(fh.filepath, as_attachment=True, attachment_filename=fh.file_name)


@bp.route('/submissions/<string:submission_id>/files/<string:file_id>', methods=['DELETE'])
def delete_file(submission_id, file_id):
    """Delete a given file that was perviously uploaded for a submission. The
    user has to be a member of the submission in order to be allowed to delete
    files.

    Parameters
    ----------
    submission_id: string
        Unique submission identifier
    file_id: string
        Unique file identifier

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
        api.submissions().delete_file(
            submission_id=submission_id,
            file_id=file_id,
            user=api.authenticate(request)
        )
    return make_response(jsonify(dict()), 204)
