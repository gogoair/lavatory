"""Unit tests for Artifactory Module."""

from unittest import mock
from lavatory.utils.artifactory import Artifactory


@mock.patch('lavatory.utils.artifactory.party.Party.get')
@mock.patch('lavatory.utils.artifactory.load_credentials')
def test_list(mock_load_credentials, mock_party_request):
    credentials = {'artifactory_password': 'test_password',
                   'artifactory_url': 'test_url',
                   'artifactory_username': 'test_username'}
    data = {
        'repositoriesSummaryList': [{
            'repoKey': 'test-local',
            'repoType': 'LOCAL'
        }]
    }
    mock_load_credentials.return_value = credentials
    mock_party_request.return_value.json.return_value = data

    repos = Artifactory()
    art = repos.list()

    assert art['test-local'] == {'repoKey': 'test-local', 'repoType': 'LOCAL'}
