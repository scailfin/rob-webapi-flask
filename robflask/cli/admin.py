# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Command line interface for the administrative tasks to intialize and maintain
the Reproducible Open Benchmark (ROB) Web API.
"""

import click

from robcore.config.install import DB
from robflask.cli.benchmark import benchmarkcli

import robcore.core.util as util
import robflask.config as config
import robflask.error as err


@click.group()
def cli():
    """Command line interface for administrative tasks to manage the
    Reproducible Open Benchmarks (ROB) Web API.
    """
    pass


@cli.command()
@click.option(
    '-d', '--dir',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help='Base directory for API files (overrides ROB_API_DIR).'
)
@click.option(
    '-f', '--force',
    is_flag=True,
    default=False,
    help='Create database without confirmation'
)
def init(dir=None, force=False):
    """Initialize database and base directories for the Reproducible Open
    Benchmarks (ROB) Web API. The configuration parameters for the database
    are taken from the respective environment variables. Creates the API base
    directory if it does not exist.
    """
    if not force:
        click.echo('This will erase an existing database.')
        click.confirm('Continue?', default=True, abort=True)
    # Create a new instance of the database
    try:
        DB.init()
    except err.MissingConfigurationError as ex:
        click.echo(str(ex))
    # If the base directory is given ensure that the directory exists
    if not dir is None:
        base_dir = dir
    else:
        base_dir = config.API_BASEDIR()
    if not base_dir is None:
        util.create_dir(base_dir)


# Benchmarks
cli.add_command(benchmarkcli)
