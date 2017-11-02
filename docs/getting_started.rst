Getting Started
===============

Authentication
--------------

Lavatory looks for 3 enviroment variables in order to authenticate:

``ARTIFACTORY_URL`` - Base URL to use for Artifactory connections

``ARTIFACTORY_USERNAME`` - Username to Artifactory

``ARTIFACTORY_PASSWORD`` - Password for Artifactory

These will be loaded in at the beginning of a run and raise an exception
if missing.

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
      --repo TEXT               Name of specific repository to run against. Can
                                use --repo multiple times. If not provided, uses
                                all repos.
      --help                    Show this message and exit.

If you want to run Lavatory against a specific repository, you can use ``--repo <repo_name>``.
You can specify ``--repo`` as multiple times to run against multiple repos. If ``--repo`` is not
provided, Lavatory will run against all repos in Artifactory.  

By default, Lavatory runs in drymode. Must include ``--nodryrun`` in order to
actually delete Artifacts

CLI Help
--------

You can run any Lavatory command with ``--help`` for assistance.

Verbosity
~~~~~~~~~

Adding ``lavatory -v $command`` will increase logging verbosity.
You can add up to 5 ``v`` like ``lavatory -vvvvv $command`` for maximum
verbosity. 

