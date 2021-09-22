===============
Version History
===============

v0.6.2
======
* Updated unit tests to use salobj.CscBaseTestCase
* Added pytest-black
* Updated schema to current format
* Fixed missing await in ApplyPositionLimits
* Removed docker folder and Jenkinsfile.deploy that were deprecated by the cycle build system.
* Removed Travis CI file
* Rename bin script to run_athexapod.py
* Added missing softwareVersions field

v0.6.1
======
* Changed Jenkinsfile.conda to use Jenkins Shared Library
* Pinned ts-idl and ts-salobj versions in conda recipe

v0.6.0
------
* Added compatibility with ts_salobj v6

v0.5.0
------
* Jenkinsfile updates
* Expand and modernize the documentation
* Expand the unit tests

v0.4.1
------
* Added Jenkinsfile for conda recipe
* Added conda recipe
* Fixed setup.py
* Fixed setup.cfg

v0.4.1_rc1
----------
* Added Jenkinsfile for conda recipe
* Added conda recipe
* Fixed setup.py
* Fixed setup.cfg

v0.4.0
------
* Rewrite CSC for salobj 5
* Add mock server for unit tests
* Rewrite controller
* Bring into flake8 compliance

v0.3.0
------
* Revamp for salobj 4
* Fix wait_movement_done method
* initial_simulation_mode to simulation_mode

v0.2.0
------
* fix bugs
* add more hexapod controller support
* add simulation mode

v0.1.0
------
* initial release
