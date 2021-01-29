# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019-2021 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for API helper functions."""

import pytest

import robflask.api.util as util
import robflask.error as err


class FakeRequest(object):
    """Fake request object with json property that is None."""
    json = None


def test_jsonbody_errors():
    """Test error condition for the jsonbody helper function."""
    # Error when passing an object that has no json attribute
    with pytest.raises(err.InvalidRequestError):
        util.jsonbody(list())
    with pytest.raises(err.InvalidRequestError):
        util.jsonbody(FakeRequest())
