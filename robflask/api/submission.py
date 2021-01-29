# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Blueprint for submission resources."""

from flask import Blueprint, jsonify, make_response, request

from flowserv.error import UnknownUserError

from robflask.api.util import ACCESS_TOKEN, jsonbody

import flowserv.view.group as labels
import robflask.config as config
import robflask.error as err


bp = Blueprint('submissions', __name__, url_prefix=config.API_PATH())


@bp.route('/workflows/<string:workflow_id>/groups', methods=['POST'])
def create_submission(workflow_id):
    """Create a new submission for a given benchmark. The user has to be
    authenticated in order to be able to create a new submission.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Verify that the request contains a valid Json object that contains the
    # submission name and an optional list of member identifier.
    obj = jsonbody(
        request,
        mandatory=[labels.GROUP_NAME],
        optional=[labels.GROUP_MEMBERS]
    )
    name = obj[labels.GROUP_NAME]
    members = obj.get(labels.GROUP_MEMBERS)
    if members is not None and not isinstance(members, list):
        raise err.InvalidRequestError('{} not a list'.format(labels.GROUP_MEMBERS))
    from robflask.service import service
    with service(access_token=token) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        try:
            r = api.groups().create_group(
                workflow_id=workflow_id,
                name=name,
                members=members
            )
        except UnknownUserError as ex:
            # Change error type from unknown object to invalid request if a
            # user in the member list is unknown
            raise err.InvalidRequestError(str(ex))
    return make_response(jsonify(r), 201)


@bp.route('/groups/<string:group_id>', methods=['DELETE'])
def delete_submission(group_id):
    """Delete the submission with the given identifier. The user has to be a
    submission member in order to be authorized to delete the submission.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        api.groups().delete_group(group_id=group_id)
    return make_response(jsonify(dict()), 204)


@bp.route('/groups/<string:group_id>', methods=['GET'])
def get_submission(group_id):
    """Get handle for the submission with the given identifier. The user has to
    be authenticated in order to access a submission.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        r = api.groups().get_group(group_id=group_id)
    return make_response(jsonify(r), 200)


@bp.route('/workflows/<string:workflow_id>/groups', methods=['GET'])
def list_submission(workflow_id):
    """Get a list of all submissions for a given benchmark. The user has to be
    authenticated in order to be able to access the submission list.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    from robflask.service import service
    with service(access_token=ACCESS_TOKEN(request)) as api:
        r = api.groups().list_groups(workflow_id=workflow_id)
    return make_response(jsonify(r), 200)


@bp.route('/groups/<string:group_id>', methods=['PUT'])
def update_submission(group_id):
    """Update the submission with the given identifier. The request body can
    contain a modified submission name and/or a modified list of submission
    members.
    """
    # Get the access token first to raise an error immediately if no token is
    # present (to avoid unnecessarily instantiating the service API).
    token = ACCESS_TOKEN(request)
    # Verify that the request contains a valid Json object that contains an
    # optional submission name and/or a list of member identifier.
    obj = jsonbody(
        request,
        mandatory=[],
        optional=[labels.GROUP_NAME, labels.GROUP_MEMBERS]
    )
    name = obj.get(labels.GROUP_NAME)
    members = obj.get(labels.GROUP_MEMBERS)
    from robflask.service import service
    with service(access_token=token) as api:
        # Authentication of the user from the expected api_token in the header
        # will fail if no token is given or if the user is not logged in.
        r = api.groups().update_group(
            group_id=group_id,
            name=name,
            members=members
        )
    return make_response(jsonify(r), 200)
