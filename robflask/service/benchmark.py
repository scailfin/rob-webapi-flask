# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Modified implementation for the API benchmark component.
"""


class BenchmarkService(object):
    """API component that provides methods to access benchmarks and benchmark
    leader boards.
    """
    def __init__(self, workflow_service, submission_service):
        """Initialize the workflow service from the flowServ API and the
        modified submission service.

        Parameters
        ----------
        workflow_service: flowserv.service.workflow.WorkflowService
             Workflow service from the flowServ API
        """
        self.workflow_service = workflow_service
        self.submission_service = submission_service

    def get_benchmark(self, benchmark_id, user_id):
        """Get serialization of the handle for the given benchmark. The
        modified benchmark handle contains serialized descriptors for all
        submissions that the given user has for the benchmark.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier
        user_id: string
            Unique identifier for the user that is requesting the submission
            listing

        Returns
        -------
        dict

        Raises
        ------
        flowserv.error.UnknownBenchmarkError
        """
        # Get the default handle first
        doc = self.workflow_service.get_workflow(workflow_id=benchmark_id)
        # Add submission descriptors if the user identifier is given
        if user_id is not None:
            submissions = self.submission_service.list_submissions(
                benchmark_id=benchmark_id,
                user_id=user_id
            )
            doc['submissions'] = submissions['submissions']
        else:
            doc['submissions'] = list()
        return doc

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
        flowserv.error.UnknownWorkflowError
        """
        return self.workflow_service.get_ranking(
            workflow_id=benchmark_id,
            order_by=order_by,
            include_all=include_all
        )

    def get_result_archive(self, benchmark_id):
        """Get compressed tar-archive containing all result files that were
        generated by the most recent post-processing workflow. If the benchmark
        does not have a post-processing step or if the post-processing run is
        not in SUCCESS state, a unknown resource error is raised.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier

        Returns
        -------
        io.BytesIO

        Raises
        ------
        flowserv.error.UnknownWorkflowError
        flowserv.error.UnknownResourceError
        """
        return self.workflow_service.get_result_archive(
            workflow_id=benchmark_id
        )

    def get_result_file(self, benchmark_id, file_id):
        """Get file handle for a resource file that was generated as the result
        of a successful benchmark post-processing run.

        Parameters
        ----------
        benchmark_id: string
            Unique benchmark identifier
        file_id: string
            Unique resource file identifier

        Returns
        -------
        flowserv.model.base.FileHandle

        Raises
        ------
        flowserv.error.UnknownWorkflowError
        flowserv.error.UnknownResourceError
        """
        return self.workflow_service.get_result_file(
            workflow_id=benchmark_id,
            file_id=file_id
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
        return self.workflow_service.list_workflows()
