"""Test statistics function."""
import pytest
from unittest import mock

from lavatory.utils.artifactory import Artifactory


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
    artifactory_class = Artifactory(repo_name='test-local')
    return artifactory_class


@mock.patch('lavatory.utils.artifactory.party.Party.request')
def test_stats(mock_party_request, artifactory):
    data = {
        'repositoriesSummaryList': [{
            'repoKey': 'test-local',
            'repoType': 'LOCAL',
            'foldersCount': 473,
            'filesCount': 5915,
            'usedSpace': '105.59 GB',
            'itemsCount': 6388,
            'packageType': 'Test',
            'percentage': '8.05%'
        }]
    }
    mock_party_request.return_value.json.return_value = data
    art = artifactory.get_statistics()

    assert art is True
    assert isinstance(art, bool)
