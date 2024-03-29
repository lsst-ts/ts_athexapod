.. _Developer_Guide:

#########################
ATHexapod Developer Guide
#########################
.. image:: https://img.shields.io/badge/GitHub-ts_athexapod-green.svg
    :target: https://github.com/lsst-ts/ts_athexapod
.. image:: https://img.shields.io/badge/Jenkins-ts_athexapod-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_athexapod/
.. image:: https://img.shields.io/badge/Jira-ts_athexapod-green.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_athexapod
.. image:: https://img.shields.io/badge/ts_xml-ATHexapod-green.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/ATHexapod.html


The CSC is implemented using the salobj library for integration with the middleware layer.

The architecture of the Hexapod control software is a TCP/IP connection with a particular messaging format.
You can find in the `PI-824 manual <https://docushare.lsst.org/docushare/dsweb/Get/Document-21614>`__
where it describes this format.


.. _Dependencies:

Dependencies
============

* `SAL <https://ts-sal.lsst.io>`_ - v4.0.0
* ts_salobj - v5.2.0
* python - 3.7.x
* lsstts/develop-env:b76

.. toctree::
    :maxdepth: 1

    ../changelog

.. _API:

ATHexapod API
=============
The content in this section is autogenerated from docstrings.

.. .. uml:: state-diagram.plantuml

.. automodapi:: lsst.ts.athexapod
    :no-main-docstr:
    :no-inheritance-diagram:

.. _Build:

Build and Test
==============

A note before beginning to develop this package.
Install Docker as this is required.

This package has the following requirements:

* Docker
* ts_Dockerfiles - lsstts/develop-env:b76(stable) or lsstts/develop-env:develop(bleeding edge)

.. We should link to a description of the development container once there is a place for it.

Build the CSC as follows:

.. code-block:: bash

    docker run -it -v {repos_location}:/home/saluser/develop lsstts/develop-env:b76
    make_idl_files.py ATHexapod
    cd develop/ts_athexapod
    setup -kr .
    scons



.. _Usage:

Usage
=====

Starting the CSC is done by using the following command.

.. prompt:: bash

    python bin/runATHexapodCSC.py

Stopping the CSC is done by SIG-INTing the process, usually by :kbd:`ctrl` + :kbd:`c`

Running the unit tests can be done from the top-level directory of the repository by invoking

.. prompt:: bash
    
    pytest


.. _Simulator:

Simulator
=========
There is a vendor provided simulator that can be started as a docker container.
Since this is proprietary, the image is private and so to get access, send a request on slack to couger01 with your username on DockerHub.
Then use docker to sign into your dockerhub credentials with the following command.

.. prompt:: bash

    docker login
    # give username and password

Then pulling and running the image will work.

.. this throws a warning but I'm not sure why.

.. prompt:: bash

    docker run --net host -it couger01/hexapod_simulator

Stopping the CSC is done by SIG-INTing the process, usually by :kbd:`ctrl` + :kbd:`c`

.. _Troubleshooting:

Troubleshooting
===============


Serial Connection
-----------------

There is a known issue with the internal firmware and the PiMikroMove software where the serial connection capability does not work.
However, it is possible to connect using PiTerminal, which is installed on the lenovo (windows) machine (which can be reached via remote desktop to aux-brick01.cp.lsst.org).

The serial connection uses a <LF> line termination for the command and receive terminations. 
The default baud is 115200, data bits 8, stop bits 1, parity none, handshake (flow control) none (in the PI terminal)
C877 manual says that the handshake is cts/rts, but if this is enabled then the computer can send commands but does not receive responses.

Sending ``*IDN?<LF>`` should return something like "(c)2011-2019 Physik Instrumente (PI) GmbH & Co. KG,C-887,116027371,2.7.1.4"
Sending ``IFS?`` returns the communication settings.
Again, RSHSHK return 1, which corresponds to rts/cts, but this setting does not work.

Successful connections to the device have been made via teraterm, but the serial and terminal settings must be correct.
In setup->Terminal, make sure Receive and Transmit are set to LF; the Local-echo box should also be checked.
In Setup->Serial Port, input the settings above.
If any changes are made, the connection must be disconnected and reconnected.

However, `YAT (yet another terminal) <https://sourceforge.net/projects/y-a-terminal/>`_ seems able to send but not receive responses; this is probably a setup issue but it's not yet been identified.

TCP/IP connection
-----------------

The hexapod has a DNS name (``athexapod.cp.lsst.org``) and reserved DHCP address registered in our network, therefore, a reserved IP inside the hexapod itself should not be required.
This means that the parameter ``IPSTART`` should be set to ``1`` to use the DHCP settings and not a manually assigned IP at the controller level.
This can be performed either via the PIMikroMove software or using the terminal.
A reset of the controller is required for the new settings to take effect.


.. _Contributing:

Contributing
============

Code and documentation contributions utilize pull-requests on github.
Feature requests can be made by filing a Jira ticket with the `ts_athexapod` label.
In all cases, reaching out to the :ref:`contacts for this CSC <Contact_Personnel>` is recommended.

.. _Firmware:

Updating Firmware For ATHexapod
===============================

Instructions on updating the firmware can be found in `chapter 10 of the PI-824 manual <https://docushare.lsst.org/docushare/dsweb/Get/Document-21614>`_.
As an aside, upgrading the firmware is difficult and can result in problems if not performed correctly.
It is strongly encouraged to only upgrade if the vendor is recommending this be performed.


.. _Documentation:

Building the Documentation
==========================


Pull the develop-env docker image (the example below uses cycle ``c25``, revision ``5``, but this should be changed to the current release), mounting the repository directory as a volume.
Then building the documentation is done by the following commands.

.. prompt:: bash

    docker run -it -v {repo_location}:/home/saluser/develop lsstts/develop-env:c0025.005 
    cd develop/ts_athexapod
    setup -kr . # or pip install .
    scons # this step is optional if using pip
    pip install -r doc/requirements.txt
    package-docs build


