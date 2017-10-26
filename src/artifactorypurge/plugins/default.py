
def purgelist(artifactory, repo, project):
    return artifactory.retain(repo, project, depth=2, terms=[
            { "$or": [
                ]}
        ])
