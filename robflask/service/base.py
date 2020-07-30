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

from flowserv.model.database import DB
from flowserv.service.api import API
from flowserv.view.factory import DefaultView
from robflask.service.benchmark import BenchmarkService
from robflask.service.submission import SubmissionService


LABELS = dict({
    'GROUPS': {
        'GROUP_LIST': 'submissions',
        'WORKFLOW_ID': 'benchmark'
    },
    'RUNS': {
        'RUN_GROUP': 'submission',
        'RUN_WORKFLOW': 'benchmark'
    },
    'WORKFLOWS': {
        'WORKFLOW_GROUP': 'submission',
        'WORKFLOW_LIST': 'benchmarks'
    }
})


class WebAPI(API):
    """The API object implements a factory pattern for all API components. The
    individual components are instantiated on-demand to avoid any overhead for
    components that are not required to handle a user request.
    """
    def __init__(self, session):
        """Initialize the database connection and the serialization labels.

        Parameters
        ----------
        session: sqlalchemy.orm.session.Session
            Database session.
        """
        super(WebAPI, self).__init__(
            session=session,
            view=DefaultView(labels=LABELS)
        )

    def benchmarks(self):
        """Get instance of the benchmark service component.

        Returns
        -------
        robflask.service.benchmark.BenchmarkService
        """
        return BenchmarkService(
            workflow_service=self.workflows(),
            submission_service=self.submissions()
        )

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
        robflask.service.submission.SubmissionService
        """
        return SubmissionService(
            group_service=self.groups(),
            run_service=self.runs()
        )


# -- API constructor ----------------------------------------------------------

webdb = DB(web_app=True)


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
    with webdb.session() as session:
        yield WebAPI(session=session)
