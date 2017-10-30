
def purgelist(artifactory):
    purgable = artifactory.count_based_retention(retention_count=5)
    return purgable