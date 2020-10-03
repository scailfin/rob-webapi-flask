# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for uploads and downloads of files that are associated with
submissions.
"""

from flask import Blueprint, jsonify, make_response, request, send_file
from werkzeug.utils import secure_filename

from flowserv.model.files.base import FlaskFile
from robflask.api.auth import ACCESS_TOKEN

import flowserv.config.api as config
import robflask.error as err


bp = Blueprint('uploads', __name__, url_prefix=config.API_PATH())


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
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownFileError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    from robflask.service.base import service
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.uploads().list_uploaded_files(
            group_id=submission_id,
            user_id=api.authenticate(token).user_id
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
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownFileError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Ensure that the upload request contains a file object
    if request.files and 'file' in request.files:
        file = request.files['file']
        # A browser may submit a empty part without filename
        if file.filename == '':
            raise err.InvalidRequestError('empty file name')
        # Save uploaded file to a bytes buffer.
        filename = secure_filename(file.filename)
        from robflask.service.base import service
        with service() as api:
            # Authentication of the user from the expected api_token in the
            # header will fail if the user is not logged in.
            r = api.uploads().upload_file(
                group_id=submission_id,
                file=FlaskFile(file),
                name=filename,
                user_id=api.authenticate(token).user_id
            )
        return make_response(jsonify(r), 201)
    else:
        raise err.InvalidRequestError('no file request')


@bp.route(
    '/submissions/<string:submission_id>/files/<string:file_id>',
    methods=['GET']
)
def download_file(submission_id, file_id):
    """Download a given file that was perviously uploaded for a submission.

    NOTE: At this point, the user is not authenticated for file downloads to
    allow download in the GUI via browser redirect.

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
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownFileError
    """
    from robflask.service.base import service
    with service() as api:
        fh = api.uploads().get_uploaded_file(
            group_id=submission_id,
            file_id=file_id
        )
        return send_file(
            fh.open(),
            as_attachment=True,
            attachment_filename=fh.name,
            mimetype=fh.mime_type
        )


@bp.route(
    '/submissions/<string:submission_id>/files/<string:file_id>',
    methods=['DELETE']
)
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
    flowserv.error.UnauthenticatedAccessError
    flowserv.error.UnauthorizedAccessError
    flowserv.error.UnknownFileError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    from robflask.service.base import service
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        api.uploads().delete_file(
            group_id=submission_id,
            file_id=file_id,
            user_id=api.authenticate(token).user_id
        )
    return make_response(jsonify(dict()), 204)
