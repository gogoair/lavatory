"""Unit tests for testing retention functions"""

import pytest
from unittest import mock

from lavatory.utils.artifactory import Artifactory

TEST_ARTIFACT1 = {'name': 'test1', 'path': '/path/to/test/1'}
TEST_ARTIFACT2 = {'name': 'test2', 'path': '/path/to/test/2'}


@pytest.fixture
def artifactory(mock_credentials):
    creds = {
        'artifactory_password': 'test_password',
        'artifactory_url': 'test_url',
        'artifactory_username': 'test_username'
    }

    mock_credentials.return_value = creds
    artifactory = Artifactory()
    return artifactory


@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
@mock.patch('lavatory.utils.artifactory.party.Party.get_properties')
def test_get_all_artifacts(mock_properties, mock_find_aql, artifactory):
    """Tests get_all_repo_artifacts returns all artifacts."""
    test_artifacts = {'results': [TEST_ARTIFACT2, TEST_ARTIFACT1]}
    mock_find_aql.return_value = test_artifacts

    expected_return = [TEST_ARTIFACT2, TEST_ARTIFACT1]
    artifacts = artifactory.get_all_repo_artifacts()
    assert artifacts == expected_return


@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
def test_count_based_retention(mock_find_aql, artifactory):
    """Tests count base retention returns values"""
    test_artifacts = {'results': [TEST_ARTIFACT2, TEST_ARTIFACT1]}
    mock_find_aql.return_value = test_artifacts

    # deplicates values because of nested search at project level. Expected
    expected_return = [TEST_ARTIFACT2, TEST_ARTIFACT1, TEST_ARTIFACT2, TEST_ARTIFACT1]
    purgable = artifactory.count_based_retention(retention_count=1)
    assert purgable == expected_return


@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
def test_time_based_retention(mock_find_aql, artifactory):
    """Tests count base retention returns values"""
    test_artifacts = {'results': [TEST_ARTIFACT2, TEST_ARTIFACT1]}
    mock_find_aql.return_value = test_artifacts

    expected_return = [TEST_ARTIFACT2, TEST_ARTIFACT1]
    purgable = artifactory.time_based_retention(keep_days=10)
    assert purgable == expected_return
