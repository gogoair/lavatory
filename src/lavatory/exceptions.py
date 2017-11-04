"""Lavatory related custom exceptions"""


class LavatoryError(Exception):
    """Lavatory related error"""


class MissingEnvironmentVariable(LavatoryError):
    """Required environment variable is missing"""

    def __init__(self, missing_var):
        error = 'Missing Environement variable {0}.'.format(missing_var)
        super().__init__(error)


class InvalidPoliciesDirectory(LavatoryError):
    """Extra policies directory is invalid or missing"""
