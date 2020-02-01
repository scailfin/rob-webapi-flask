# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper methods to test object serialization."""

from flowserv.tests.serialize import validate_run_handle

import flowserv.core.util as util


# -- Benchmarks ---------------------------------------------------------------

def validate_benchmark_handle(doc):
    """Validate serialization of a benchmark handle.

    Parameters
    ----------
    doc: dict
        Benchmark handle serialization

    Raises
    ------
    ValueError
    """
    mandatory = ['id', 'name', 'parameters']
    optional = ['description', 'instructions', 'postproc', 'modules']
    util.validate_doc(doc=doc, mandatory=mandatory, optional=optional)
    # Validate the post-processing run handle if present
    if 'postproc' in doc:
        postproc = doc['postproc']
        validate_run_handle(doc=postproc, state=postproc['state'])


def validate_benchmark_listing(doc):
    """Validate serialization of a benchmark descriptor listing.

    Parameters
    ----------
    doc: dict
        Serialization for listing of benchmark descriptors

    Raises
    ------
    ValueError
    """
    util.validate_doc(doc=doc, mandatory=['benchmarks'])
    for b in doc['benchmarks']:
        util.validate_doc(
            doc=b,
            mandatory=['id', 'name'],
            optional=['description', 'instructions']
        )


# -- Submissions --------------------------------------------------------------

def validate_submission_handle(doc):
    """Validate serialization of a submission handle.

    Parameters
    ----------
    doc: dict
        Submission handle serialization

    Raises
    ------
    ValueError
    """
    util.validate_doc(
        doc=doc,
        mandatory=['id', 'name', 'benchmark', 'members', 'parameters', 'files']
    )


def validate_submission_listing(doc):
    """Validate serialization of a submission listing.

    Parameters
    ----------
    doc: dict
        Listing of submission descriptor serializations

    Raises
    ------
    ValueError
    """
    util.validate_doc(doc=doc, mandatory=['submissions'])
    for s in doc['submissions']:
        util.validate_doc(doc=s, mandatory=['id', 'name', 'benchmark'])


# -- Rankings -----------------------------------------------------------------

def validate_ranking(doc):
    """Validate serialization of a workflow evaluation ranking.

    Parameters
    ----------
    doc: dict
        Ranking serialization

    Raises
    ------
    ValueError
    """
    util.validate_doc(
        doc=doc,
        mandatory=['schema', 'ranking'],
        optional=['postproc']
    )
    # Schema columns
    for col in doc['schema']:
        util.validate_doc(doc=col, mandatory=['id', 'name', 'type'])
    # Run results
    for entry in doc['ranking']:
        util.validate_doc(doc=entry, mandatory=['run', 'group', 'results'])
        util.validate_doc(
            doc=entry['run'],
            mandatory=['id', 'createdAt', 'startedAt', 'finishedAt']
        )
        util.validate_doc(doc=entry['group'], mandatory=['id', 'name'])
        for result in entry['results']:
            util.validate_doc(doc=result, mandatory=['id', 'value'])


# -- Service descriptor -------------------------------------------------------

def validate_service_descriptor(doc):
    """Validate serialization of the service descriptor.

    Parameters
    ----------
    doc: dict
        Service descriptor serialization

    Raises
    ------
    ValueError
    """
    util.validate_doc(
        doc=doc,
        mandatory=['name', 'version', 'validToken'],
        optional=['username']
    )
