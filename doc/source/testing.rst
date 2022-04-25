=============
Running tests
=============


redfish module tests
--------------------

Tests are not functional for the redfish module yet.

redfish-client tests
--------------------

#. Create your development environment following `Developer setup <http://pythonhosted.org/python-redfish/develsetup.html>`_.
#. Install docker using the `procedure <https://docs.docker.com/engine/installation/>`_.
#. Ensure you can use docker with your current user.
#. Jump into the python-redfish directory containing the source code.
#. Depending of your distribution, you may have to upgrade setuptools::

    pip install --upgrade setuptools

#. Install required modules for testings::

    pip install -t test-requirements.txt

#. Run the test::

    tox

   or::

    py.test redfish-client

