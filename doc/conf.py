"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ts.ATHexapod


_g = globals()
_g.update(
    build_package_configs(
        project_name="ts_ATHexapod", version=lsst.ts.ATHexapod.version.__version__
    )
)
extensions.append("sphinx-jsonschema")
# extensions.append("sphinxcontrib.plantuml")
# extensions.append("releases")
# releases_issue_uri = "https://jira.lsstcorp.org/browse/%s"
# comment out releases_release_uri until feature for prefix and unreleased develop url is merged
# releases_release_uri = "https://github.com/lsst-ts/ts_salobjATHexapod/tree/v%s"
