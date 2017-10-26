"""ArtifactoryPurge related custom exceptions"""

class MissingEnvironmentVariable(Exception):
    def __init__(self, missing_var):
        error = 'Missing Environement variable {0}.'.format(missing_var)
        super().__init__(error)
