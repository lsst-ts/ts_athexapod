============
ts_ATHexapod
============

General Overview
================

.. image:: https://img.shields.io/badge/GitHub-ts_athexapod-green.svg
    :target: https://github.com/lsst-ts/ts_athexapod
.. image:: https://img.shields.io/badge/Jenkins-ts_athexapod-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_athexapod/
.. image:: https://img.shields.io/badge/Jira-ts_athexapod-green.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_athexapod
.. image:: https://img.shields.io/badge/ts_xml-ATHexapod-green.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/ATHexapod.html

ts_ATHexapod is a python package that implements the CSC for the ATHexapod.
It is written using the `ts_salobj <https://ts-salobj.lsst.io>`_ library.
It can be installed as an EUPS package or as a PIP package.

Software Documentation
======================
Pull the develop-env docker image.
Mount the repo directory as a volume.
The architecture of the Hexapod control software is a tcp/ip connection with a particular messaging format.
You can find in the manual where it describes this format.
The CSC is implemented using the salobj library for integration with the middleware layer.

Dependencies
------------
* `SAL <https://ts-sal.lsst.io>`_ - v4.0.0
* ts_salobj - v5.2.0
* python - 3.7.x
* lsstts/develop-env:b76

.. toctree::
    :maxdepth: 1

    changelog


.. .. uml:: state-diagram.plantuml

.. automodapi:: lsst.ts.ATHexapod
    :no-main-docstr:
    :no-inheritance-diagram:

User Documentation
==================
First open a remote using salobj.
There are multiple ways to do this.
Its very likely that you will use a jupyter notebook of some kind to interact with an individual CSC.

.. prompt:: bash

    ipython

.. code::

    from lsst.ts import salobj
    athexapod = salobj.Remote("ATHexapod", salobj.Domain())
    await salobj.set_summary_state(athexapod, salobj.State.ENABLED)
    await athexapod.cmd_moveToPosition.set_start(x=1, y=1, z=1, u=1, v=1, w=1, timeout=5)

Sending commands, you follow the same format as shown above `await athexapod.cmd_{nameOfCommand}.set_start(parameters, timeout)`
Receiving events, you follow this format `await athexapod.evt_{nameOfEvent}.aget()`
Receiving telemetry, you follow this format `await athexapod.tel_{nameOfTelemetry}.aget()`

