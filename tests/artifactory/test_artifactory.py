"""Unit tests for Artifactory Module."""

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


@mock.patch('lavatory.utils.artifactory.party.Party.request')
def test_list(mock_party_request, artifactory):
    data = {'repositoriesSummaryList': [{'repoKey': 'test-local', 'repoType': 'LOCAL'}]}
    mock_party_request.return_value.json.return_value = data
    art = artifactory.list()

    assert art['test-local'] == {'repoKey': 'test-local', 'repoType': 'LOCAL'}


@mock.patch('lavatory.utils.artifactory.party.Party.get_properties')
def test_get_artifact_properties(mock_properties, artifactory):
    test_artifact = {"name": "test", "path": "path/to/test"}
    props = artifactory.get_artifact_properties(test_artifact)
    assert props == TEST_PROPS

@mock.patch('lavatory.utils.artifactory.party.Party.post')
def test_move_artifacts(artifactory):
    test_artifacts = [{"name": "test", "path": "path/to/test"},
                      {"name": "test2", "path": "path/to/test2"}]
    moved = artifactory.move_artifacts(artifacts=test_artifacts,
                                       dest_repository='test_repo')
    assert moved

