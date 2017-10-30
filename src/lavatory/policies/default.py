
def purgelist(artifactory):
    return artifactory.retain(None, depth=2, terms=[
            {"$or": [
                ]}
        ])
