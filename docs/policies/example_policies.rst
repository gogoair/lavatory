Example Policies
----------------

Below are some example plugins, starting with simple ones and then
showing some complex examples.

Time Based Retention
~~~~~~~~~~~~~~~~~~~~

This policy will purge any artifact in the repository older than 120 days.

::

    def purgelist(artifactory):
        """Policy to purge all artifacts older than 120 days"""
        purgable = artifactory.time_based_retention(keep_days=120)
        return purgable

Count Based Retention
~~~~~~~~~~~~~~~~~~~~~

This policy will retain the last 5 artifacts of each project in a repository.

::

    def purgelist(artifactory):
        """Policy to keep just the 5 most recent artifacts."""
        purgable = artifactory.count_based_retention(retention_count=5)
        return purgable

