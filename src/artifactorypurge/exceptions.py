"""ArtifactoryPurge related custom exceptions"""

class MissingEnvironmentVariable(Exception):
    """Required environment variable is missing"""
    def __init__(self, missing_var):
        error = 'Missing Environement variable {0}.'.format(missing_var)
        super().__init__(error)
