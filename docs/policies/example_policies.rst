Example Policies
================

.. toctree::
   :maxdepth: 2
   
.. contents::
   :local:

These are example policies for different retention use-cases

Keep last 120 days of artifacts
-------------------------------

::

    def purgelist(artifactory):
        """Policy to purge all artifacts older than 120 days"""
        purgable = artifactory.time_based_retention(keep_days=120)
        return purgable


Keep artifacts downloaded in the last 60 days
---------------------------------------------

::

    def purgelist(artifactory):
        """Policy to purge all artifacts not downloaded in last 60 days"""
        purgeable = artifactory.time_based_retention(keep_days=60, time_field='stat.downloaded')
        return purgeable


Keep 5 most recent artifacts
----------------------------

::

    def purgelist(artifactory):
        """Policy to keep just the 5 most recent artifacts."""
        purgeable = artifactory.count_based_retention(retention_count=5)
        return purgeable


Keep artifacts with specific properties
---------------------------------------

::

    def purgelist(artifactory):
        """Policy to purge artifacts with deployed property of dev and not prod."""
        aql_terms = [{"@deployed": {"$match": "dev"}}, {"@deployed": {"$nmatch": "prod"}}]
        extra_fields = ['property.*']
        purgeable = artifactory.filter(terms=aql_terms, fields=extra_fields, depth=None, item_type="any")
        return purgeable

Keep all artifacts
------------------

::

    def purgelist(artifactory):
        """Keep artifacts indefinitely."""
        return []

Move artifacts to a different repo after 3 days.
------------------------------------------------

::

    def purgelist(artifactory):
        """Moves artifacts to yum-local after 3 days."""
        movable = artifactory.time_based_retention(keep_days=3)
        artifactory.move_artifacts(artifacts=movable, dest_repository='yum-local')
        return []


More complicated examples
--------------------------

::

    def purgelist(artifactory):
        """Purges artifacts that have not been downloaded in the last month,
        That do not have a build.correlation_id,
        and are not in the */latest path."""

        docker_terms = [ { "stat.downloaded": { "$before": "1mo" }},
                        { "@build.correlation_ids": { "$nmatch": "*" }},
                        { "name": { "$match": "manifest.json" }},
                        { "path": { "$nmatch": "*/latest" }}
                    ]
        purgeable = artifactory.filter(terms=docker_terms, depth=None, item_type="file")

        return purgeable

::

    def purgelist(artifactory):
        """If deployed to prod, keep artifact forever,
        if deployed to stage, keep 30 days,
        if deployed to dev, keep 21 days,
        if never deployed, keep 30 days."""

        not_deployed = [ { "@deployed": { "$nmatch": "*" }}]

        only_dev =  [ { "@deployed": { "$match": "*dev*"} },
                    { "@deployed": {"$nmatch": "*prod*"} },
                    { "@deployed": { "$nmatch": "*stage*"} }
                    ]

        only_stage =  [ { "@deployed": { "$match": "*stage*"} },
                        { "@deployed": {"$nmatch": "*prod*"} },
                    ]

        undeployed_purgeable = artifactory.time_based_retention(keep_days=30, extra_aql=not_deployed)
        only_dev_purgeable = artifactory.time_based_retention(keep_days=21, extra_aql=only_dev)
        only_stage_purgeable = artifactory.time_based_retention(keep_days=30, extra_aql=only_dev)

        all_purgeable = undeployed_purgeable + only_dev_purgeable + only_stage_purgeable
        return all_purgeable