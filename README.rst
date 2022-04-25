The python-redfish project
==========================

This repository will be used to house the python-redfish library, a reference
implementation to enable Python developers to communicate with the Redfish API
(http://www.dmtf.org/standards/redfish).

NOTE::

    STATUS: Work in progress, ready for proof of concept.

    The current Redfish specification revision is 1.0.0 - Note that the mockup
    is still at version 0.99.0a and may not reflect what the standard provides
    fully. And please check the version before you use it.

Documentation
-------------

The full documentation is available at
http://pythonhosted.org/python-redfish/installation.html

Project Structure
-----------------

This project follows the same convention as OpenStack projects, eg. using pbr
for build and test automation::

    doc/            # Documentation
    doc/source      # The doc source files live here
    doc/build/html  # Output of building any docs will go here
    dmtf            # Reference documents and mockup provided by the DMTF
    examples/       # Any sample code using this library, eg. for education
                    # should be put here
    pbconf          # Project builder file to build rpm/deb packages for
                    # distributions
    redfish/        # The redfish library itself
    redfish/tests/  # python-redfish unit test suite
    redfish-client  # Client tool to manage redfish devices

Requirements
------------

To use the enclosed examples, you will need Python 2.7 or Python 3.4
(https://www.python.org/downloads/).  Note that Python 2.7.9 enforces greater
SSL verification requiring server certificates be installed. Parameters to
relax the requirements are available in the library, but these configurations
are discouraged due to security.

Python requirements are listed in requirements.txt. Additional requirements for
running the unit test suite are listed in test-requirements.txt.

Note: Running tests requires Docker engine.

Note: The program was tested with Python 2.7.10 and 3.4.2 however it might work
as well with all Python 3 releases.

Get the source code
-------------------

The source code is available on github and can be retrieved using::

    git clone https://github.com/openstack/python-redfish.git

Installation
------------

Please refer to the following link.

http://pythonhosted.org/python-redfish/installation.html

Contacts
--------

Distribution list: python-redfish@mondorescue.org

Further References
------------------

Please look at `dmtf/README.rst <https://github.com/bcornec/python-redfish/blob/master/dmtf/README.rst>`_ file.
