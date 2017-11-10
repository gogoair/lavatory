Policy Helpers
--------------

Below are some helper functions to assist in writing policies. These include
easy ways to do time-based retention, count-based retention, or searching with AQL.

Time Based Retention
~~~~~~~~~~~~~~~~~~~~

This policy will purge any artifact in the repository older than 120 days.

::

    def purgelist(artifactory):
        """Policy to purge all artifacts older than 120 days"""
        purgable = artifactory.time_based_retention(keep_days=120)
        return purgable

.. automethod:: lavatory.utils.artifactory.Artifactory.time_based_retention


Count Based Retention
~~~~~~~~~~~~~~~~~~~~~

This policy will retain the last 5 artifacts of each project in a repository.

::

    def purgelist(artifactory):
        """Policy to keep just the 5 most recent artifacts."""
        purgable = artifactory.count_based_retention(retention_count=5)
        return purgable

.. automethod:: lavatory.utils.artifactory.Artifactory.count_based_retention


AQL Filtering
~~~~~~~~~~~~~

You can also use AQL to search for artifacts if you need more control than the
count-based retention or time-based retention helps.

::

    def purgelist(artifactory):
        """Policy to purge artifacts with deployed property of dev and not prod."""
        aql_terms = [{"@deployed": {"$match": "dev"}}, {"@deployed": {"$nmatch": "prod"}}]
        extra_fields = ['property.*']
        purgable = artifactory.filter(terms=aql_terms, fields=extra_fields, depth=None, item_type="any")
        return purgable

All of the terms in ``aql_terms`` will be ``ANDed`` together and searched.

The above policy would use the below full AQL to search for artifacts.

::

    items.find({"$and": [{"@deployed": {"$match": "dev"}},
               {"@deployed": {"$nmatch": "prod"}}, {"path": {"$nmatch": "*/repodata"}},
               {"repo": {"$eq": "yum-local"}}, {"type": {"$eq": "any"}}]}).include("stat", "property.*")


.. automethod:: lavatory.utils.artifactory.Artifactory.filter
