Example Policies
================

These are example policies for different retention use-cases

Keep last 120 days of artifacts
-------------------------------

::

    def purgelist(artifactory):
        """Policy to purge all artifacts older than 120 days"""
        purgable = artifactory.time_based_retention(keep_days=120)
        return purgable


Keep 5 most recent artifacts
----------------------------

::

    def purgelist(artifactory):
        """Policy to keep just the 5 most recent artifacts."""
        purgable = artifactory.count_based_retention(retention_count=5)
        return purgable


Keep artifacts with specific properties
---------------------------------------

::

    def purgelist(artifactory):
        """Policy to purge artifacts with deployed property of dev and not prod."""
        aql_terms = [{"@deployed": {"$match": "dev"}}, {"@deployed": {"$nmatch": "prod"}}]
        extra_fields = ['property.*']
        purgable = artifactory.filter(terms=aql_terms, fields=extra_fields, depth=None, item_type="any")
        return purgable

