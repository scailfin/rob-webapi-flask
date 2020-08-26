# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) [2019-2020] NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Helper methods to test object serialization."""

from flowserv.tests.serialize import (
    validate_parameter, validate_run_descriptor
)

import flowserv.util as util
import flowserv.model.workflow.state as st


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
    mandatory = ['id', 'name', 'parameters', 'submissions']
    optnl = ['description', 'instructions', 'postproc', 'modules', 'outputs']
    util.validate_doc(doc=doc, mandatory=mandatory, optional=optnl)
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
        optional=['postproc', 'outputs']
    )
    # Schema columns
    for col in doc['schema']:
        util.validate_doc(doc=col, mandatory=['id', 'name', 'dtype'])
    # Run results
    for entry in doc['ranking']:
        util.validate_doc(
            doc=entry,
            mandatory=['run', 'submission', 'results']
        )
        util.validate_doc(
            doc=entry['run'],
            mandatory=['id', 'createdAt', 'startedAt', 'finishedAt']
        )
        util.validate_doc(doc=entry['submission'], mandatory=['id', 'name'])
        for result in entry['results']:
            util.validate_doc(doc=result, mandatory=['id', 'value'])


# -- Runs ---------------------------------------------------------------------

def validate_run_handle(doc, state):
    """Validate serialization of a run handle.

    Parameters
    ----------
    doc: dict
        Run handle serialization
    state: string
        Expected run state

    Raises
    ------
    ValueError
    """
    labels = ['id', 'benchmark', 'state', 'createdAt', 'arguments']
    if state == st.STATE_RUNNING:
        labels.append('startedAt')
    elif state in [st.STATE_ERROR, st.STATE_CANCELED]:
        labels.append('startedAt')
        labels.append('finishedAt')
        labels.append('messages')
    elif state == st.STATE_SUCCESS:
        labels.append('startedAt')
        labels.append('finishedAt')
        labels.append('files')
    util.validate_doc(
        doc=doc,
        mandatory=labels,
        optional=['parameters', 'submission']
    )
    if 'parameters' in doc:
        for p in doc['parameters']:
            validate_parameter(p)
    assert doc['state'] == state
    keys = ['self']
    if state in st.ACTIVE_STATES:
        keys.append('self:cancel')
    else:
        keys.append('self:delete')
    if state == st.STATE_SUCCESS:
        keys.append('results')
        for r in doc['files']:
            util.validate_doc(doc=r, mandatory=['id', 'name'])


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
        mandatory=['name', 'version', 'validToken', 'routes'],
        optional=['username']
    )
    for r in doc['routes']:
        util.validate_doc(doc=r, mandatory=['action', 'pattern'])


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
        mandatory=[
            'id',
            'name',
            'benchmark',
            'members',
            'parameters',
            'files',
            'runs'
        ]
    )
    for run in doc['runs']:
        validate_run_descriptor(doc=run)


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
