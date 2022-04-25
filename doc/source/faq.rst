===
FAQ
===

- Q1 : error in setup command: Invalid environment marker: (python_version < '3')

    This error is caused by an old setuptools version that does not understand "python_version < '3'".
    Upgrade setuptools using::

        pip install --upgrade setuptools

