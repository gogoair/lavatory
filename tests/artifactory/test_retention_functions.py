"""Unit tests for testing retention functions"""

import pytest
from unittest import mock

from lavatory.utils.artifactory import Artifactory

TEST_PROPS = {'build': 1, 'other': 'test'}


@pytest.fixture
@mock.patch('lavatory.utils.artifactory.load_credentials')
@mock.patch('lavatory.utils.artifactory.party.Party.request')
def artifactory(mock_party, mock_credentials):
    creds = {
        'artifactory_password': 'test_password',
        'artifactory_url': 'test_url',
        'artifactory_username': 'test_username'
    }

    mock_credentials.return_value = creds
    artifactory = Artifactory()
    artifactory.artifactory.properties = TEST_PROPS
    return artifactory


@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
@mock.patch('lavatory.utils.artifactory.party.Party.get_properties')
def test_get_all_artifacts(mock_properties, mock_find_aql, artifactory):
    """Tests get_all_repo_artifacts returns all artifacts sorted"""
    test_artifacts = {
        'results': [{
            'name': 'test2',
            'path': '/path/to/test/2'
        }, {
            'name': 'test1',
            'path': '/path/to/test/1'
        }]
    }
    mock_find_aql.return_value = test_artifacts

    expected_return = [{
        'name': 'test1',
        'path': '/path/to/test/1'
    }, {
        'name': 'test2',
        'path': '/path/to/test/2'
    }]
    artifacts = artifactory.get_all_repo_artifacts()
    assert artifacts == expected_return


@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
def test_count_based_retention(mock_find_aql, artifactory):
    """Tests count base retention returns sorted values"""
    test_artifacts = {
        'results': [{
            'name': 'test2',
            'path': '/path/to/test/2'
        }, {
            'name': 'test1',
            'path': '/path/to/test/1'
        }]
    }
    mock_find_aql.return_value = test_artifacts

    # deplicates values because of nested search at project level. Expected
    expected_return = [{
        'name': 'test1',
        'path': '/path/to/test/1'
    }, {
        'name': 'test1',
        'path': '/path/to/test/1'
    }, {
        'name': 'test2',
        'path': '/path/to/test/2'
    }, {
        'name': 'test2',
        'path': '/path/to/test/2'
    }]
    purgable = artifactory.count_based_retention(retention_count=1)
    assert purgable == expected_return


@mock.patch('lavatory.utils.artifactory.party.Party.get_properties')
def test_get_artifact_properties(mock_properties, artifactory):
    test_artifact = {"name": "test", "path": "path/to/test"}
    props = artifactory.get_artifact_properties(test_artifact)
    assert props == TEST_PROPS
