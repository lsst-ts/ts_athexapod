"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.conf.pipelinespkg import *  # noqa
import lsst.ts.ATHexapod  # noqa

project = "ts_athexapod"
html_theme_options["logotext"] = project  # noqa
html_title = project
html_short_title = project
doxylink = {}
