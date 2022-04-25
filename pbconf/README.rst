Packaging the python-redfish project
====================================

Overview
--------

This docuemnt provides information with regards to the packagin of
python-redfish for Linux distributions. Currently the Linux distributions we
are supporting and packaging for are:

- Mageia 5
- Fedora 25
- CentOS 7
- OpenSUSE 42.2
- Debian 8
- Ubuntu 16.04

Requirements
------------

python-redfish uses a lot of python modules, not all of them having been
packaged for Linux distributions. The one missing the most being
python-tortilla, so we are providing versions for this pending distributions
doing it themselves.

Status for supported distributions
----------------------------------

- Mageia

  There are many python modules missing for Mageia 5 that have been built and 
  made avaible alongside our packages through at 
  ftp://ftp.project-builder.org/mageia/5/x86_64
  All packages needed are part of the distribution starting with version 6.

- Fedora

  Only two packages are missing on Fedora 25 python-simplejson 3.8.1 and 
  python-tortilla that are avaible alongside our packages through dnf at
  ftp://ftp.project-builder.org/fedora/25/x86_64

- CentOS

  There are many python modules missing for CentOS 7 that have been built and 
  made avaible alongside our packages through at 
  ftp://ftp.project-builder.org/centos/7/x86_64

- OpenSUSE

  There are some python modules missing for OpenSUSE 42.2 that have been built
  and made avaible alongside our packages through at 
  ftp://ftp.project-builder.org/opensuse/42.2/x86_64

- Debian

  TBD

- Ubuntu

  TBD
