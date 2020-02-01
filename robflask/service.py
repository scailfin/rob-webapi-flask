# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper classes method to create instances of the Web API components. All
components use the same underlying database connection. The connection object
is under the control of of a context manager to ensure that the connection is
closed properly after every API request has been handled.

The WebAPI class extends the default API class of flowServ with serializers
that are specific to ROB.
"""

from contextlib import contextmanager

from flowserv.core.db.driver import DatabaseDriver
from flowserv.service.api import API
from flowserv.view.factory import DefaultView


LABELS = dict()


class WebAPI(API):
    """The API object implements a factory pattern for all API components. The
    individual components are instantiated on-demand to avoid any overhead for
    components that are not required to handle a user request.
    """
    def __init__(self, con):
        """Initialize the database connection and the URL factory. The URL
        factory is kept as a class property since every API component will
        have an instance of this class.

        Parameters
        ----------
        con: DB-API 2.0 database connection
            Connection to underlying database
        """
        super(WebAPI, self).__init__(con=con, view=DefaultView(labels=LABELS))

    def benchmarks(self):
        """Get instance of the benchmark service component.

        Returns
        -------
        robcore.service.benchmark.BenchmarkService
        """
        return BenchmarkService(self.workflows())

    def service_descriptor(self, access_token):
        """Get the serialization of the service descriptor. If the request
        contains an access token it is verified that the token is still
        active.

        Parameters
        ----------
        access_token: string, optional
            API access token to authenticate the user

        Returns
        -------
        dict
        """
        return self.server(access_token).service_descriptor()

    def submissions(self):
        """Get instance of the submission service component.

        Returns
        -------
        robcore.service.submission.SubmissionService
        """
        return SubmissionService(self.groups())


# -- API components -----------------------------------------------------------

class BenchmarkService(object):
    """API component that provides methods to access benchmarks and benchmark
    leader boards.
    """
    def __init__(self, workflows):
        """Initialize the workflow service from the flowServ API.

        Parameters
        ----------
        workflows: flowserv.service.workflow.WorkflowService
             Workflow service from the flowServ API
        """
        self.workflows = workflows

    def get_benchmark(self, benchmark_id):
        """Get serialization of the handle for the given benchmark.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier

        Returns
        -------
        dict

        Raises
        ------
        flowserv.core.error.UnknownBenchmarkError
        """
        return self.workflows.get_workflow(workflow_id=benchmark_id)

    def get_leaderboard(self, benchmark_id, order_by=None, include_all=False):
        """Get serialization of the leader board for the given benchmark.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier
        order_by: list(flowserv.model.template.schema.SortColumn), optional
            Use the given attribute to sort run results. If not given the
            schema default attribute is used
        include_all: bool, optional
            Include at most one entry per submission in the result if False

        Returns
        -------
        dict

        Raises
        ------
        flowserv.core.error.UnknownWorkflowError
        """
        return self.workflows.get_leaderboard(
            workflow_id=benchmark_id,
            order_by=order_by,
            include_all=include_all
        )

    def list_benchmarks(self):
        """Get serialized listing of all benchmarks in the repository.

        Parameters
        ----------
        access_token: string, optional
            User access token

        Returns
        -------
        dict
        """
        return self.workflows.list_workflows()


class SubmissionService(object):
    """API component that provides methods to access benchmark submissions and
    their runs.
    """
    def __init__(self, groups):
        """Initialize the workflow group manager from the flowServ API.

        Parameters
        ----------
        groups: flowserv.service.group.WorkflowGroupService
            Workflow group manager from the flowServ API
        """
        self.groups = groups

    def create_submission(
        self, benchmark_id, name, user_id, parameters=None, members=None
    ):
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
        parameters: dict(string:flowserv.model.template.parameter.base.TemplateParameter), optional
            Workflow template parameter declarations
        members: list(string), optional
            List of user identifier for submission members

        Returns
        -------
        dict

        Raises
        ------
        flowserv.core.error.ConstraintViolationError
        flowserv.core.error.UnknownWorkflowError
        """
        return self.groups.create_group(
            workflow_id=benchmark_id,
            name=name,
            user_id=user_id,
            parameters=parameters,
            members=members
        )

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
        flowserv.core.error.UnauthorizedAccessError
        flowserv.core.error.UnknownWorkflowGroupError
        """
        # Raise an error if the user is not authorized to delete the submission
        # or if the submission does not exist
        self.groups.delete_group(group_id=submission_id, user_id=user_id)

    def get_submission(self, submission_id):
        """Get handle for submission with the given identifier.

        Parameters
        ----------
        submission_id: string
            Unique submission identifier

        Returns
        -------
        dict

        Raises
        ------
        flowserv.core.error.UnknownWorkflowGroupError
        """
        return self.groups.get_group(group_id=submission_id)

    def list_submissions(self, benchmark_id=None, user_id=None):
        """Get a listing of all submissions. If the user handle is given the
        result contains only those submissions that the user is a member of.
        If the benchmark identifier is given the result contains submissions
        only for the given benchmark.

        Parameters
        ----------
        benchmark_id: string, optional
            Unique benchmark identifier
        user_id: string
            Unique identifier for the user that is requesting the submission
            listing

        Returns
        -------
        dict
        """
        return self.groups.list_groups(
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
        flowserv.core.error.ConstraintViolationError
        flowserv.core.error.UnauthorizedAccessError
        flowserv.core.error.UnknownSubmissionError
        """
        return self.groups.update_group(
            group_id=submission_id,
            user_id=user_id,
            name=name,
            members=members
        )


# -- API constructor ----------------------------------------------------------

@contextmanager
def service():
    """The local service function is a context manager for an open database
    connection that is used to instantiate the user service class for the ROB
    API. The context manager ensures that the database conneciton in closed
    after a API request has been processed.

    Returns
    -------
    robflask.service.API
    """
    con = DatabaseDriver.get_connector().connect()
    yield WebAPI(con)
    con.close()
