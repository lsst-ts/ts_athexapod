..
  This is a template for documentation that will accompany each CSC.
  It consists of a user guide and development guide, however, cross linking between the guides is expected.
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
.. |CSC_developer| replace::  *Eric Coughlin <ecoughlin@lsst.org>*
.. |CSC_product_owner| replace:: *Patrick Ingraham <pingraham@lsst.org>*

.. Note that the ts_ prefix is omitted from the title

#########
ATHexapod
#########

.. image:: https://img.shields.io/badge/GitHub-ts_athexapod-green.svg
    :target: https://github.com/lsst-ts/ts_athexapod
.. image:: https://img.shields.io/badge/Jenkins-ts_athexapod-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_athexapod/
.. image:: https://img.shields.io/badge/Jira-ts_athexapod-green.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels+%3D+ts_athexapod
.. image:: https://img.shields.io/badge/ts_xml-ATHexapod-green.svg
    :target: https://ts-xml.lsst.io/sal_interfaces/ATHexapod.html

.. _Overview:

Overview
========

.. This section is to present an overview of the CSC.
.. This should include a top-level description of the primary use-case(s) as well as any pertinent information.
.. Example information may be link(s) to the higher-level classes which may be used to operate it, or mention of other CSCs (with links) that it operates in concert with.

The ATHexapod is a python package that implements the CSC that controls a `PI H-824 hexapod <https://www.pi-usa.us/en/products/6-axis-hexapods-parallel-positioners/h-824-6-axis-hexapod-700815/>`__ that holds the secondary mirror on the Auxiliary Telescope.
The hexapod allows precise positioning of the mirror, which is key to performing optical collimation of the telescope as well as focus adjustments.
It is written using the `ts_salobj <https://ts-salobj.lsst.io>`_ library. It can be installed as an EUPS package or as a PIP package.

Under normal operations, it is expected that the CSC will be largely controlled from commands received from the ATAOS and essentially no direct user interaction is required.
The ATHexapod is also part of the `ATCS high-level control package <https://obs-controls.lsst.io/System-Architecture/Control-Packages/index.html>`__.

The badges above navigate to the GitHub repository for the CSC code, Jenkins CI jobs, Jira issues and communications interface for the software.

.. _User_Documentation:

User Documentation
==================
User-level documentation, found at the link below, is aimed at personnel looking to perform the standard use-cases/operations with the ATHexapod.

.. toctree::
    user-guide/user-guide
    :maxdepth: 2

.. _Configuration:

Configuring the ATHexapod
=========================
.. For CSCs where configuration is not required, this section can contain a single sentence stating so.
   More introductory information can also be added here (e.g. CSC XYZ requires both a configuration file containing parameters as well as several look-up tables to be operational).

The configuration for the ATHexapod is described at the following link.

.. toctree::
    configuration/configuration
    :maxdepth: 1

.. _Development_Documentation:

Development Documentation
=========================
This area of documentation focuses on the classes used, API's, and how to participate to the development of the ATHexapod software packages.

.. toctree::
    developer-guide/developer-guide
    :maxdepth: 1


.. _Version_History:

Version History
===============
The version history of the ATHexapod CSC is found at the following link.

.. toctree::
    changelog
    :maxdepth: 1

`Release notes <https://github.com/lsst-ts/ts_athexapod/releases>`__ have not yet been published for this package, but will be in the future.

.. _Contact_Personnel:

Contact Personnel
=================

For questions not covered in the documentation, emails should be addressed to |CSC_developer| and |CSC_product_owner|.

This procedure was last modified |today|.

