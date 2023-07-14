"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

import lsst.ts.athexapod  # noqa
from documenteer.conf.pipelinespkg import *  # noqa

project = "ts_athexapod"
html_theme_options["logotext"] = project  # noqa
html_title = project
html_short_title = project
doxylink = {}
