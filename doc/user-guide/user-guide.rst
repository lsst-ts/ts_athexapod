..
  This is a template for the user-guide documentation that will accompany each CSC.
  This template is provided to ensure that the documentation remains similar in look, feel, and contents to users.
  The headings below are expected to be present for all CSCs, but for many CSCs, additional fields will be required.

  ** All text in square brackets [] must be re-populated accordingly **

  See https://developer.lsst.io/restructuredtext/style.html
  for a guide to reStructuredText writing.

  Use the following syntax for sections:

  Sections
  ========

  and

  Subsections
  -----------

  and

  Subsubsections
  ^^^^^^^^^^^^^^

  To add images, add the image file (png, svg or jpeg preferred) to the
  images/ directory. The reST syntax for adding the image is

  .. figure:: /images/filename.ext
     :name: fig-label

  Caption text.

  Feel free to delete this instructional comment.

.. Fill out data so contacts section below is auto-populated
.. add name and email between the *'s below e.g. *Marie Smith <msmith@lsst.org>*
.. |CSC_developer| replace::  *Replace-with-name-and-email*
.. |CSC_product_owner| replace:: *Replace-with-name-and-email*

.. _User_Guide:

####################
ATHexapod User Guide
####################
.. image:: https://img.shields.io/badge/GitHub-ts_athexapod-green.svg
    :target: https://github.com/lsst-ts/ts_athexapod
.. image:: https://img.shields.io/badge/Jenkins-ts_athexapod-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_athexapod/
.. image:: https://img.shields.io/badge/Jira-ts_athexapod-green.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_athexapod
.. image:: https://img.shields.io/badge/ts_xml-ATHexapod-green.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/ATHexapod.html

The ATHexapod CSC is generally commanded by the ATAOS to maintain the collimation of the telescope, compensating for gravitational deformations of the structure as it moves in elevation.
The ATAOS also applies focus offsets whenever required, but via the `ATCS high-level control package <https://obs-controls.lsst.io/System-Architecture/Control-Packages/index.html>`__.
Details on telescope collimation and the relationship between hexapod motion and induced Wavefront Error are found in two technotes.

#. `Using CWFS during operations and for collimation of the Auxiliary Telescope <https://tstn-015.lsst.io/>`__
#. `Auxiliary Telescope: Determining sensitivity matrix for hexapod correction using CWFS data <https://tstn-016.lsst.io/>`__

The CSC itself is can be commanded directly, but make sure the ATAOS corrections are disabled prior to interacting with it.
Note that specification of the rotation should be avoiding as the mirror is rotationally symmetric, therefore specifying rotation will only limit hexapod motion and result in increased times to reach a desired location.
Also, after a power cycle, the hexapod will need to be homed, this is done automatically as part of the standard state transitions.

ATHexapod Interface
===================

The full set of commands, events and telemetry are found in the `ts_xml repository <https://ts-xml.lsst.io/sal_interfaces/ATHexapod.html>`__ (also linked from the green button at the top of the page).

The principal use-case for this CSC is the regular adjustment between desired positions, either providing absolute positions or relative offsets to the current position.

Moving to an absolute position utilizes the ``moveToPosition`` command, which accepts desired positions in 6 degrees of freedom (x, y, z, u, v ,w).
Offsets to the current position using the ``applyPositionOffset`` command.
In all cases, positions are in `mm` and `degrees`.
The ``inPosition`` event flips to ``False`` when in motion, or not in the commanded position.
Upon reaching a position, the ``inPosition`` event flips to ``True`` and the ``positionUpdate`` event which gives the current hexapod position, as read by the hexapod encoders.

Although not often required, the ATHexapod publishes the demanded position, current position, and position error for all axes as telemetry in the ``positionStatus`` topic.


Example Use-Case
================

The standard use-case, as mentioned above, is to command the hexapod to a given position.

There are multiple ways to perform this, likely it would be inside a high-level package, but it also can be done from a jupyter notebook, or the ipython command line. Here we assume the ipython command line will be used, as it generalizes to the other methods.s

First open a remote using salobj, then bring the CSC to the enabled state.
There are multiple ways to do this.

.. prompt:: bash

    ipython

.. code:: python

    from lsst.ts import salobj
    athexapod = salobj.Remote("ATHexapod", salobj.Domain())
    await salobj.set_summary_state(athexapod, salobj.State.ENABLED)
    await athexapod.cmd_moveToPosition.set_start(x=1, y=1, z=1, u=1, v=1, w=1, timeout=5)

The offset command (and all others) follows the same format as shown above. To offset the hexapod you would replace the `nameOfCommand` with `applyPositionOffset` and substitute `parameters` for the positions of each axis.

.. code:: python

    await athexapod.cmd_{nameOfCommand}.set_start(parameters, timeout)

Receiving events, you follow the format below, where the ``positionUpdate`` event gives the most recent position.
Of course, this syntax is generic and can be replaced with any other event.

.. code:: python

    await athexapod.evt_positionUpdate.aget()

Receiving telemetry, you follow a similar format, where ``positionStatus`` reports the demanded position, current position, and position error for all axes at an interval of 1s.

.. code:: python

    await athexapod.tel_spositionStatus.aget()


