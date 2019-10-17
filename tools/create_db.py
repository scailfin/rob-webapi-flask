# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Create a new instance of the ROB database. The database connection
information is expected to be given in the respective environment variables.
"""


from robcore.config.install import DB


if __name__ == '__main__':
    DB.init()
