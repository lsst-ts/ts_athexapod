#######################
ATHexapod Configuration
#######################

Configuration is handled using yaml files located in a git repository, `ts_config_attcs <https://github.com/lsst-ts/ts_config_attcs>`__.
Generally, the only value that may require changing is the IP address.

However, more configuration parameters are available, as described by the schema found in the `ts_athexapod repository <https://github.com/lsst-ts/ts_athexapod>`__.

One item worth noting is that although there are software limits on the hexapod motion, the hexapod has sufficient clearance such that it can move over the full range without interfering with any nearby surface.

..
  What follows is the current schema that these configuration files can have.

  .. jsonschema:: ../../schema/ATHexapod.yaml