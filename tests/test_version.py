# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019-2021 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit test for version string (for completeness)."""

from robflask.version import __version__


def test_version_stirng():
    """Ensure that the version string is set."""
    assert __version__ is not None
