|Build Status| |Doc Status|


Lavatory
========

Tooling to define repository specific retention policies in Artifactory.
Allows highly customizable retention policies via Python plugins.

This tool is an Work in Progres! Not ready for production use!

Requirements
~~~~~~~~~~~~

-  Python 3.4+
-  Artifactory user with API permissions

Authentication
~~~~~~~~~~~~~~

This tool looks for 3 enviroment variables in order to authenticate:

``ARTIFACTORY_URL`` - Base URL to use for Artifactory connections

``ARTIFACTORY_USERNAME`` - Username to Artifactory

``ARTIFACTORY_PASSWORD`` - Password for Artifactory

These will be loaded in at the beginning of a run and raise an exception
if missing.

Installing
~~~~~~~~~~

From pypi:

``pip install lavatory``

Or install directly from the code:

::

    git clone https://github.com/gogoair/lavatory
    cd lavatory
    pip install -U .

Running
~~~~~~~

::

    $ lavatory --help
    Usage: lavatory [OPTIONS] COMMAND [ARGS]...

      Lavatory is a tool for managing Artifactory Retention Policies

    Options:
      -v, --verbose  Increases logging level
      --help         Show this message and exit.

    Commands:
      purge  Deletes artifacts based on retention policies

Purging Artifacts
-----------------

``lavatory purge --policies-path=/path/to/policies``

::

    $ lavatory purge --help
    Usage: lavatory purge [OPTIONS]

      Deletes artifacts based on retention policies

    Options:
      --policies-path TEXT      Path to extra policies directory
      --dryrun / --nodryrun     Dryrun does not delete any artifacts. On by
                                default
      --default / --no-default  If false, does not apply default policy
      --help                    Show this message and exit.

Testing
~~~~~~~

::

    pip install -r requirements-dev.txt
    tox

.. |Build Status| image:: https://travis-ci.org/gogoair/lavatory.svg?branch=master
   :target: https://travis-ci.org/gogoair/lavatory

.. |Doc Status| image:: https://readthedocs.org/projects/lavatory/badge/?version=latest
   :target: http://lavatory.readthedocs.io/en/latest/?badge=latest