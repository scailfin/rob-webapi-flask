# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Flask Application Factory. Initalize the Flask application that serves the
ROB web API.
"""

import logging
import os

from flask import Flask, jsonify, make_response
from flask_cors import CORS
from logging.handlers import RotatingFileHandler

import robflask.error as err
import robflask.config as config


def create_app():
    """Initialize the Flask application."""
    # Create tha app. Follwoing the Twelve-Factor App methodology we configure
    # the Flask application from environment variables.
    app = Flask(__name__, instance_relative_config=True)
    # Enable CORS
    CORS(app)
    # --------------------------------------------------------------------------
    # Initialize error logging
    # --------------------------------------------------------------------------
    # Use rotating file handler for server logs
    file_handler = RotatingFileHandler(
        os.path.join(config.LOG_DIR(), 'webapi.log'),
        maxBytes=1024 * 1024 * 100,
        backupCount=20
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    app.logger.addHandler(file_handler)

    # --------------------------------------------------------------------------
    # Define error handlers
    # --------------------------------------------------------------------------
    @app.errorhandler(err.ConstraintViolationError)
    def invalid_request_action(error):
        """JSON response handler for requests that violate an application
        constraint.

        Parameters
        ----------
        error : Exception
            Exception thrown by request Handler

        Returns
        -------
        Http response
        """
        return make_response(jsonify({'message': str(error)}), 400)

    @app.errorhandler(err.InvalidRequest)
    def invalid_request_body(error):
        """JSON response handler for requests that do not contain a valid
        request body.

        Parameters
        ----------
        error : Exception
            Exception thrown by request Handler

        Returns
        -------
        Http response
        """
        return make_response(jsonify({'message': str(error)}), 400)

    @app.errorhandler(err.UnauthenticatedAccessError)
    def unauthenticated_access(error):
        """JSON response handler for unauthenticated requests.

        Parameters
        ----------
        error : Exception
            Exception thrown by request Handler

        Returns
        -------
        Http response
        """
        return make_response(jsonify({'message': str(error)}), 403)

    @app.errorhandler(err.UnknownObjectError)
    def resource_not_found(error):
        """JSON response handler for requests that access unknown resources.

        Parameters
        ----------
        error : Exception
            Exception thrown by request Handler

        Returns
        -------
        Http response
        """
        return make_response(jsonify({'message': str(error)}), 404)

    @app.errorhandler(413)
    def upload_error(error):
        """Exception handler for file uploads that exceed the file size
        limit.
        """
        app.logger.error(error)
        return make_response(jsonify({'error': str(error)}), 413)

    @app.errorhandler(500)
    def internal_error(error):
        """Exception handler that logs internal server errors."""
        app.logger.error(error)
        return make_response(jsonify({'error': str(error)}), 500)

    # --------------------------------------------------------------------------
    # Import blueprints for API components
    # --------------------------------------------------------------------------
    # Service Descriptor
    import robflask.api.descriptor as descriptor
    app.register_blueprint(descriptor.bp)
    # User Service
    import robflask.api.users as users
    app.register_blueprint(users.bp)
    # Return the app
    return app
