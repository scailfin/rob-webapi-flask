# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for functions in the config module that provide access to values
in environment variables that are used to configure the Web API.
"""

import os
import pytest

import robflask.config as config


def test_apipath():
    """Test getting the API path from the service environment."""
    assert config.API_PATH() is not None


def test_logdir():
    """Test getting the environment variable value for the logging directory
    that is used by the Flask service.
    """
    # Set the environment variable and ensure that the absolute pathname to
    # the specified directory is returned by the config LOG_DIR() function
    os.environ[config.ROB_WEBAPI_LOG] = '.log/api'
    assert config.LOG_DIR() == os.path.abspath('.log/api')
    # Clear the environment variable.
    del os.environ[config.ROB_WEBAPI_LOG]
    # The default value is a subfolder in the API base dir with name 'log'
    assert os.path.basename(config.LOG_DIR()) == 'log'


def test_max_upload_size():
    """Test accessing the maximum file size for file uploads."""
    # Set the environment variable and ensure that the respective value is
    # returned as an integer
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = '1234'
    assert config.MAX_CONTENT_LENGTH() == 1234
    # A ValueError is raised if the environment variable is set to a value
    # than cannot be converted to integer
    os.environ[config.ROB_WEBAPI_CONTENTLENGTH] = 'ABC'
    with pytest.raises(ValueError):
        config.MAX_CONTENT_LENGTH()
    # Clear the environment variable to ensure that the default value is
    # returned.
    del os.environ[config.ROB_WEBAPI_CONTENTLENGTH]
    assert config.MAX_CONTENT_LENGTH() == 16 * 1024 * 1024
