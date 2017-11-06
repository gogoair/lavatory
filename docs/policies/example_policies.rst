Policies Helpers
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

``artifactory.time_based_retention()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

time_based_retention() has the following keyword arguments:


``keep_days`` (int): Number of days to keep an artifact.

``item_type`` (str): The item type to search for (file/folder/any). 

``extra_aql`` (list). List of extra AQL terms to apply to search



Count Based Retention
~~~~~~~~~~~~~~~~~~~~~

This policy will retain the last 5 artifacts of each project in a repository.

::

    def purgelist(artifactory):
        """Policy to keep just the 5 most recent artifacts."""
        purgable = artifactory.count_based_retention(retention_count=5)
        return purgable

``artifactory.count_based_retention()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

count_based_retention() has the following keyword arguments:

``retention_count`` (int): Number of artifacts to keep.

``project_depth`` (int):  how far down the Artifactory folder hierarchy to look for projects.

``artifact_depth`` (int):  how far down the Artifactory folder hierarchy to look for specific artifacts.

``item_type`` (str): The item type to search for (file/folder/any).


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

``artifactory.filter()``
^^^^^^^^^^^^^^^^^^^^^^^^

filter() has the following keyword arguments:

``terms`` (list): an array of jql snippets that will be ANDed together

``depth`` (int, optional): how far down the folder hierarchy to look

``fields`` (list): Fields

``sort`` (dict): How to sort Artifactory results

``offset`` (int): how many items from the beginning of the list should be skipped (optional)

``limit`` (int): the maximum number of entries to return (optional)

``item_type`` (str): The itme type to search for (file/folder/any).
