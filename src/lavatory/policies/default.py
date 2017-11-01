"""Default retention policy. Keeps the last 5 artifacts from each project"""


def purgelist(artifactory):
    #purgable = artifactory.count_based_retention(retention_count=5)
    purgable = artifactory.get_all_repo_artifacts()
    return purgable
