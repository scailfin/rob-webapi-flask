# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Global instance of the API factory that is used by the Flask application to
interact with the flowserv instance.
"""

from typing import Optional

from flowserv.client.api import ClientAPI
from flowserv.config import env
from flowserv.service.api import APIFactory


# API factory that is used by the Flask App. This global variable will be set
# by the init_service() function. This separation is currently required for
# unit testing.
service = None


def init_service(basedir: Optional[str] = None, database: Optional[str] = None) -> APIFactory:
    """Configure the API factory that is used by the Flask application.

    Parameters
    ----------
    basedir: string, default=None
        Base directory for all workflow files. If no directory is given or
        specified in the environment a temporary directory will be created.
    database: string, default=None
        Optional database connect url.

    Returns
    -------
    flowserv.service.api.APIFactory
    """
    global service
    service = ClientAPI(
        env=env().auth().run_async().webapp(),
        basedir=basedir,
        database=database
    )
    return service


# Initialize the global service API factory.
service = init_service()
