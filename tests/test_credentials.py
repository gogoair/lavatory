"""Unit tests for getting credentials from environment"""

import pytest

from artifactorypurge.exceptions import MissingEnvironmentVariable
from artifactorypurge.credentials import load_credentials

def test_missing_credentials_exception(monkeypatch):
    """Tests that an exception is raised if environment variable is missing"""
    monkeypatch.setenv('ARTIFACTORY_URL', None)
    with pytest.raises(MissingEnvironmentVariable):
        load_credentials()

def test_load_credentials(monkeypatch):
    """Tests that the right environment variables are loaded and returned"""
    monkeypatch.setenv('ARTIFACTORY_URL', 'test_url')
    monkeypatch.setenv('ARTIFACTORY_PASSWORD', 'test_password')
    monkeypatch.setenv('ARTIFACTORY_USERNAME', 'test_username')
    credentials = load_credentials()
    assert credentials == {'artifactory_password': 'test_password',
                           'artifactory_url': 'test_url',
                           'artifactory_username': 'test_username'}
    
