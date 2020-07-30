# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Modified implementation for the API submission component."""


class SubmissionService(object):
    """API component that provides methods to access benchmark submissions and
    their runs.
    """
    def __init__(self, group_service, run_service):
        """Initialize the workflow group manager from the flowServ API.

        Parameters
        ----------
        group_service: flowserv.service.group.WorkflowGroupService
            Workflow group manager from the flowServ API
        run_service: flowserv.service.run.RunService
            Service component for benchmark runs
        """
        self.group_service = group_service
        self.run_service = run_service

    def create_submission(self, benchmark_id, name, user_id, members=None):
        """Create a new submission for a given benchmark. Each submission for
        the benchmark has a unique name, a submission owner, and a list of
        additional submission members.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier
        name: string
            Unique team name
        user_id: string
            Unique identifier for the submission owner
        members: list(string), optional
            List of user identifier for submission members

        Returns
        -------
        dict

        Raises
        ------
        flowserv.error.ConstraintViolationError
        flowserv.error.UnknownWorkflowError
        """
        # Get the default serialization for the submission handle
        doc = self.group_service.create_group(
            workflow_id=benchmark_id,
            name=name,
            user_id=user_id,
            members=members
        )
        # Add empty list of run handles
        doc['runs'] = list()
        return doc

    def delete_submission(self, submission_id, user_id):
        """Get a given submission and all associated runs and results. If the
        user is not an administrator or a member of the submission an
        unauthorized access error is raised.

        Parameters
        ----------
        submission_id: string
            Unique submission identifier
        user_id: string
            Unique identifier for the user that is deleting the submission

        Raises
        ------
        flowserv.error.UnauthorizedAccessError
        flowserv.error.UnknownWorkflowGroupError
        """
        # Raise an error if the user is not authorized to delete the submission
        # or if the submission does not exist
        self.group_service.delete_group(
            group_id=submission_id,
            user_id=user_id
        )

    def get_submission(self, submission_id, user_id):
        """Get handle for submission with the given identifier. Extends the
        default group handle with a list of handles for all benchmark runs.

        Parameters
        ----------
        submission_id: string
            Unique submission identifier
        user_id: string
            Unique identifier for the user that is requesting the submission
            listing

        Returns
        -------
        dict

        Raises
        ------
        flowserv.error.UnknownWorkflowGroupError
        """
        # Get the default submission handle
        doc = self.group_service.get_group(group_id=submission_id)
        # Add serialized descriptors for all submission runs
        listing = self.run_service.list_runs(
            group_id=submission_id,
            user_id=user_id
        )
        doc['runs'] = listing['runs']
        return doc

    def list_submissions(self, benchmark_id=None, user_id=None):
        """Get a listing of all submissions. If the user handle is given the
        result contains only those submissions that the user is a member of.
        If the benchmark identifier is given the result contains submissions
        only for the given benchmark.

        Parameters
        ----------
        benchmark_id: string, optional
            Unique benchmark identifier
        user_id: string, optional
            Unique identifier for the user that is requesting the submission
            listing

        Returns
        -------
        dict
        """
        return self.group_service.list_groups(
            workflow_id=benchmark_id,
            user_id=user_id
        )

    def update_submission(
        self, submission_id, user_id, name=None, members=None
    ):
        """Update the name for the team with the given identifier. The access
        token is optional to allow a super user to change team names from the
        command line interface without the need to be a team owner. A web
        service implementation should always ensure that an access token is
        given.

        Parameters
        ----------
        submission_id: string
            Unique submission identifier
        user_id: string
            Unique identifier for the user that is accessing the submission
        name: string, optional
            New submission name
        members: list(string), optional
            Modified list of team members

        Returns
        -------
        dict

        Raises
        ------
        flowserv.error.ConstraintViolationError
        flowserv.error.UnauthorizedAccessError
        flowserv.error.UnknownSubmissionError
        """
        # Update the submission. Then retrieve the modified handle
        self.group_service.update_group(
            group_id=submission_id,
            user_id=user_id,
            name=name,
            members=members
        )
        return self.get_submission(
            submission_id=submission_id,
            user_id=user_id
        )
