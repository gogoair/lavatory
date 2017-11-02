def purgelist(artifactory):
    """Default Policy. Keeps the last 5 artifacts from each project"""
    purgable = artifactory.count_based_retention(retention_count=5)
    return purgable
