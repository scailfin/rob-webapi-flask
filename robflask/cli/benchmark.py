# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Administrator command line interface to create, delete and maintain
benchmarks.
"""

import click

from robflask.service import service

import robflask.error as err


# ------------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------------

# -- Add benchmark -------------------------------------------------------------

@click.command(name='create')
@click.option(
    '-n', '--name',
    required=True,
    help='Unique benchmark name.'
)
@click.option(
    '-d', '--description',
    required=False,
    help='Short benchmark description.'
)
@click.option(
    '-i', '--instructions',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help='File containing instructions for participants.'
)
@click.option(
    '-s', '--src',
    type=click.Path(exists=True, file_okay=False, readable=True),
    required=False,
    help='Benchmark template directory.'
)
@click.option(
    '-u', '--url',
    required=False,
    help='Benchmark template Git repository URL.'
)
@click.option(
    '-f', '--specfile',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help='Optional path to benchmark specification file.'
)
def add_benchmark(
    name, description=None, instructions=None, src=None, url=None, specfile=None
):
    """Create a new benchmark."""
    # Add benchmark template to repository
    with service() as api:
        try:
            # Get the benchmark repository instance from the API
            repo = api.benchmark_repository()
            b = repo.add_benchmark(
                name=name,
                description=description,
                instructions=read_instructions(instructions),
                src_dir=src,
                src_repo_url=url,
                spec_file=specfile
            )
            click.echo('export ROB_BENCHMARK={}'.format(b.identifier))
        except (err.ConstraintViolationError, ValueError) as ex:
            click.echo(str(ex))


# -- Delete benchmark ----------------------------------------------------------

@click.command(name='delete')
@click.argument('identifier')
def delete_benchmark(identifier):
    """Delete a given benchmark."""
    with service() as api:
        try:
            repo = api.benchmark_repository()
            repo.delete_benchmark(identifier)
            click.echo('deleted benchmark {}'.format(identifier))
        except err.UnknownObjectError as ex:
            click.echo(str(ex))


# -- List benchmarks -----------------------------------------------------------

@click.command(name='list')
def list_benchmarks():
    """List all benchmarks."""
    with service() as api:
        repo = api.benchmark_repository()
        count = 0
        for bm in repo.list_benchmarks():
            if count != 0:
                click.echo()
            count += 1
            title = 'Benchmark {}'.format(count)
            click.echo(title)
            click.echo('-' * len(title))
            click.echo()
            click.echo('ID          : {}'.format(bm.identifier))
            click.echo('Name        : {}'.format(bm.name))
            click.echo('Description : {}'.format(bm.description))
            click.echo('Instructions: {}'.format(bm.instructions))


# -- Update benchmark ----------------------------------------------------------

@click.command(name='update')
@click.argument('identifier')
@click.option(
    '-n', '--name',
    required=False,
    help='Unique benchmark name.'
)
@click.option(
    '-d', '--description',
    required=False,
    help='Short description.'
)
@click.option(
    '-i', '--instructions',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=False,
    help='File containing instructions for participants.'
)
def update_benchmark(identifier, name=None, description=None, instructions=None):
    """Update benchmark properties."""
    # Ensure that at least one of the optional arguments is given
    if name is None and description is None and instructions is None:
        click.echo('nothing to update')
    else:
        with service() as api:
            repo = api.benchmark_repository()
            try:
                repo.update_benchmark(
                    benchmark_id=identifier,
                    name=name,
                    description=description,
                    instructions=read_instructions(instructions)
                )
                click.echo('updated benchmark {}'.format(identifier))
            except (err.UnknownObjectError, err.ConstraintViolationError) as ex:
                click.echo(str(ex))


# ------------------------------------------------------------------------------
# Command Group
# ------------------------------------------------------------------------------

@click.group(name='benchmarks')
def benchmarkcli():
    """Create, delete, and maintain benchmarks."""
    pass


benchmarkcli.add_command(add_benchmark)
benchmarkcli.add_command(delete_benchmark)
benchmarkcli.add_command(list_benchmarks)
benchmarkcli.add_command(update_benchmark)


# ------------------------------------------------------------------------------
# Helper Methods
# ------------------------------------------------------------------------------

def read_instructions(filename):
    """Read instruction text from a given file. If the filename is None the
    result will be None as well.

    Returns
    -------
    string
    """
    # Read instructions from file if given
    instruction_text = None
    if not filename is None:
        with open(filename, 'r') as f:
            instruction_text = f.read().strip()
    return instruction_text
