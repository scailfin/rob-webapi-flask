# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for submission resources."""

from flask import Blueprint, jsonify, make_response, request

from flowserv.core.error import UnknownUserError

from robflask.api.auth import ACCESS_TOKEN
from robflask.api.util import jsonbody
from robflask.service import service

import flowserv.config.api as config
import flowserv.model.parameter.base as pb
import robflask.error as err


"""Labels for request bodys in POST and PUT requests."""
LABEL_MEMBERS = 'members'
LABEL_NAME = 'name'
LABEL_PARAMETERS = 'parameters'


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
    flowserv.core.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Verify that the request contains a valid Json object that contains the
    # submission name and an optional list of member identifier.
    obj = jsonbody(
        request,
        mandatory=[LABEL_NAME],
        optional=[LABEL_MEMBERS, LABEL_PARAMETERS]
    )
    name = obj[LABEL_NAME]
    members = obj[LABEL_MEMBERS] if LABEL_MEMBERS in obj else None
    if members is not None and not isinstance(members, list):
        raise err.InvalidRequestError('members not a list')
    parameters = None
    if LABEL_PARAMETERS in obj:
        parameters = pb.create_parameter_index(
                obj[LABEL_PARAMETERS],
                validate=True
            )
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        try:
            r = api.submissions().create_submission(
                benchmark_id=benchmark_id,
                name=name,
                parameters=parameters,
                user_id=api.authenticate(token).identifier,
                members=members
            )
        except UnknownUserError as ex:
            # Change error type from unknown object to invalid request if a
            # user in the member list is unknown
            raise err.InvalidRequestError(str(ex))
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
    flowserv.core.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    with service() as api:
        # Authenticate the user from the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        r = api.submissions().list_submissions(
            benchmark_id=benchmark_id,
            user_id=api.authenticate(token).identifier
        )
    return make_response(jsonify(r), 200)


@bp.route('/submissions', methods=['GET'])
def list_user_submission():
    """Get a list of all submissions that the authenticated user is a member
    of.

    Returns
    -------
    flask.response_class

    Raises
    ------
    flowserv.core.error.UnauthenticatedAccessError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.submissions().list_submissions(
            user_id=api.authenticate(token).identifier
        )
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
    flowserv.core.error.UnauthenticatedAccessError
    flowserv.core.error.UnauthorizedAccessError
    flowserv.core.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        api.submissions().delete_submission(
            submission_id=submission_id,
            user_id=api.authenticate(token).identifier
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
    flowserv.core.error.UnauthenticatedAccessError
    flowserv.core.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    with service() as api:
        # Authenticate the user from the api_token in the header. This
        # will raise an exception if the user is currently not logged in.
        api.authenticate(token)
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
    flowserv.core.error.ConstraintViolationError
    flowserv.core.error.UnauthenticatedAccessError
    flowserv.core.error.UnauthorizedAccessError
    flowserv.core.error.UnknownWorkflowGroupError
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Verify that the request contains a valid Json object that contains an
    # optional submission name and/or a list of member identifier.
    obj = jsonbody(
        request,
        mandatory=[],
        optional=[LABEL_NAME, LABEL_MEMBERS]
    )
    name = obj[LABEL_NAME] if LABEL_NAME in obj else None
    members = obj[LABEL_MEMBERS] if LABEL_MEMBERS in obj else None
    with service() as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.submissions().update_submission(
            submission_id=submission_id,
            user_id=api.authenticate(token).identifier,
            name=name,
            members=members
        )
    return make_response(jsonify(r), 200)
