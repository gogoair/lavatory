"""Unit tests for getting credentials from environment"""

import pytest

from artifactorypurge.exceptions import MissingEnvironmentVariable
from artifactorypurge.credentials import load_credentials

def test_missing_credentail_exception():
    """Tests that an exception is raised if environment variable is missing"""
    with pytest.raises(MissingEnvironmentVariable):
        load_credentials()