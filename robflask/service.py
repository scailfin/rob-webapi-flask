# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper classes method to create instances of the API components. All
components use the same underlying database connection. The connection object
is under the control of of a context manager to ensure that the connection is
closed properly after every API request has been handled.
"""

import os

from contextlib import contextmanager

from robcore.controller.engine import BenchmarkEngine
from robcore.db.driver import DatabaseDriver
from robcore.model.submission import SubmissionManager
from robcore.model.template.repo.benchmark import BenchmarkRepository
from robcore.model.template.repo.fs import TemplateFSRepository
from robcore.model.user.base import UserManager
from robcore.model.user.auth import DefaultAuthPolicy
from robcore.service.benchmark import BenchmarkService
from robcore.service.run import RunService
from robcore.service.submission import SubmissionService
from robcore.service.user import UserService
from robcore.view.route import UrlFactory, HEADER_TOKEN

import robcore.util as util
import robflask.config as config
import robflask.error as err


"""Default directory names."""
# Directory for storing templates for created benchmarks. This is the base
# directory for the benchmark repository.
BENCHMARKS_DIR = 'benchmarks'
# Directory for storing files that are uploaded by users to run submissions.
UPLOAD_DIR = 'uploads'


"""Define the workflow backend as a global variable. This is necessary for the
multi-porcess backend to be able to maintain process state in between API
requests.
"""
backend = config.ROB_ENGINE()


class API(object):
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
        self.con = con
        self.urls = UrlFactory()
        # Keep a copy of objects that may be used by multiple components of the
        # API. Use the respective get method for each of them to ensure that
        # the object is instantiated before access.
        self._auth = None
        self._engine = None
        self._repo = None
        self._submissions = None

    def auth(self):
        """Get authentication handler. The object is create only once.

        Returns
        -------
        robcore.model.user.auth.Auth
        """
        if self._auth is None:
            self._auth = DefaultAuthPolicy(con=self.con)
        return self._auth

    def authenticate(self, request):
        """Authenticate the user based on the api_key that is expected in the
        header of an API request. Returns the handle for the authenticated user.

        Parameters
        ----------
        request: flask.request
            Flask request object

        Returns
        -------
        robcore.model.user.base.UserHandle

        Raises
        ------
        robcore.error.UnauthenticatedAccessError
        """
        return self.auth().authenticate(request.headers.get(HEADER_TOKEN))

    def benchmarks(self):
        """Get instance of the benchmark service component.

        Returns
        -------
        robcore.service.benchmark.BenchmarkService
        """
        return BenchmarkService(
            repo=self.benchmark_repository(),
            urls=self.urls
        )

    def benchmark_repository(self):
        """Get instance of the benchmark repository.

        Returns
        -------
        robcore.model.template.repo.benchmark.BenchmarkRepository
        """
        if self._repo is None:
            # Create an instance of the template and benchmark repository. The
            # current configuration uses the file syste repository.
            benchmark_dir = os.path.join(config.API_BASEDIR(), BENCHMARKS_DIR)
            repo = TemplateFSRepository(base_dir=util.create_dir(benchmark_dir))
            self._repo = BenchmarkRepository(con=self.con, template_repo=repo)
        return self._repo

    def engine(self):
        """Get the instance of the benchmark engine.

        Returns
        -------
        robcore.model.controller.BenchmarkEngine
        """
        if self._engine is None:
            self._engine = BenchmarkEngine(con=self.con, backend=backend)
        return self._engine

    def runs(self):
        """Get instance of the run service component.

        Returns
        -------
        robcore.service.run.RunService
        """
        return RunService(
            engine=self.engine(),
            submissions=self.submission_manager(),
            repo=self.benchmark_repository(),
            auth=self.auth(),
            urls=self.urls
        )

    def submissions(self):
        """Get instance of the submission service component.

        Returns
        -------
        robcore.service.submission.SubmissionService
        """
        return SubmissionService(
            manager=self.submission_manager(),
            auth=self.auth(),
            repo=self.benchmark_repository(),
            urls=self.urls
        )

    def submission_manager(self):
        """Get instance of the submission manager.

        Returns
        -------
        robcore.model.submission.SubmissionManager
        """
        if self._submissions is None:
            self._submissions = SubmissionManager(
                con=self.con,
                directory=os.path.join(config.API_BASEDIR(), UPLOAD_DIR),
                engine=self.engine()
            )
        return self._submissions

    def users(self):
        """Get instance of the user service component.

        Returns
        -------
        robcore.service.user.UserService
        """
        return UserService(
            manager=UserManager(con=self.con),
            urls=self.urls
        )


# -- Helper methods for API request handling -----------------------------------

def jsonbody(request, mandatory_labels=None, optional_labels=None):
    """Get JSON object from the body of an API request. Validates the object
    based on the given (optional) lists of mandatory and optional labels.

    Returns the JSON object (dictionary). Raises an error if an invalid request
    or body is given.

    Parameters
    ----------
    request: flask.request
        HTTP request
    mandatory_labels: list(string)
        List of mandatory labels for the dictionary serialization
    optional_labels: list(string), optional
        List of optional labels for the dictionary serialization

    Returns
    -------
    dict

    Raises
    ------
    robflask.error.InvalidRequest
    """
    # Verify that the request contains a valid Json object
    if not request.json:
        raise err.InvalidRequest('no JSON object')
    try:
        obj = util.validate_doc(
            request.json,
            mandatory_labels=mandatory_labels,
            optional_labels=optional_labels
        )
    except ValueError as ex:
        raise err.InvalidRequest(str(ex))
    return obj


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
    yield API(con)
    con.close()
