# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

""""Unit tests for routes that serve the UI files."""


def test_ui_files(client):
    """Test accessing UI files."""
    # -- Get the UI index file ------------------------------------------------
    url = 'rob-ui'
    r = client.get(url)
    assert r.status_code == 308
    # -- Get image file -------------------------------------------------------
    url = 'rob-ui/index.html'
    r = client.get(url)
    assert r.status_code == 200
