============
ts_ATHexapod
============

The badges below are for finding the GitHub repo, Jenkins CI jobs, Jira issues and commands, events and
telemetry for the software.

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

Developer Documentation
=======================
Pull the develop-env docker image.
Mount the repo directory as a volume.
Building the documentation is done by the following commands.
Incidentally, also starts the CSC environment for you.

.. prompt:: bash
    
    docker run -it -v {repo_location}:/home/saluser/develop lsstts/develop-env:b76
    cd develop/ts_athexapod
    setup -kr . # or pip install .
    scons # this step is optional if using pip
    pip install -r doc/requirements.txt
    package-docs build

The architecture of the Hexapod control software is a tcp/ip connection with a particular messaging format.
You can find in the `manual <https://docushare.lsst.org/docushare/dsweb/Get/Document-21614>`_
where it describes this format. 
The CSC is implemented using the salobj library for integration with the middleware layer.
There is a vendor provided simulator that can be started as a docker container.
Since this is proprietary, the image is private and so to get access, send a request on slack to couger01 with your username on DockerHub.
Then use docker to sign into your dockerhub credentials with the following command.

.. prompt:: bash
    docker login
    # give username and password

Then pulling and running the image will work.

.. prompt:: bash
    
    docker run --net host -it couger01/hexapod_simulator

Starting the CSC is done by using the following command.

.. prompt:: bash
    
    python bin/runATHexapodCSC.py

Stopping the CSC is done by SIG-INTing the process, usually by :kbd:`ctrl` + :kbd:`c`

Running the unit tests can be done by invoking

.. prompt:: bash
    pytest

Updating the firmware can be found in the ATHexapod manual linked above in chapter 10.
As an aside, upgrading the firmware is difficult, so only upgrade if the vendor is recommending this.

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

.. code:: python

    from lsst.ts import salobj
    athexapod = salobj.Remote("ATHexapod", salobj.Domain())
    await salobj.set_summary_state(athexapod, salobj.State.ENABLED)
    await athexapod.cmd_moveToPosition.set_start(x=1, y=1, z=1, u=1, v=1, w=1, timeout=5)

Sending commands, you follow the same format as shown above 
.. code:: python
    
    await athexapod.cmd_{nameOfCommand}.set_start(parameters, timeout)

Receiving events, you follow this format 
.. code:: python

    await athexapod.evt_{nameOfEvent}.aget()

Receiving telemetry, you follow this format 
.. code:: python

    await athexapod.tel_{nameOfTelemetry}.aget()

Configuration
=============
Configuration is handled using yaml files located in a git repository.
The repository is called ts_config_attcs.
What follows is the current schema that these configuration files can have.

.. jsonschema:: ../schema/ATHexapod.yaml

