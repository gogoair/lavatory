How To Create Releases
----------------------

Setup
=====

Add the following to ``~/.pypirc`` file

.. code-block:: ini

    [distutils]
    index-servers =
        pypi

    [pypi]
    repository = https://pypi.python.org/pypi
    username = username
    password = xxxyyyzzz

Upload Release
==============

When releasing a new version, the following needs to occur:

#. Ensure all test via ``tox`` pass
#. Add version Tag

   .. code:: bash

      git tag -a v#.#.#
      git push --tags

#. Generate and upload the package

   .. code:: bash

      python3 setup.py bdist_wheel upload -r pypi
