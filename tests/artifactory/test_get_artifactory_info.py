from unittest import mock

from lavatory.utils.get_artifactory_info import get_artifactory_info


@mock.patch('lavatory.utils.get_artifactory_info.Artifactory')
def test_list(mock_artifactory):
    data = {'test-local': {'repoKey': 'test-local', 'repoType': 'LOCAL'}}
    mock_artifactory.return_value.list.return_value = data

    storage_list, keys = get_artifactory_info()

    assert storage_list == data
    assert 'test-local' in keys
    assert 'random-local' not in keys
    assert isinstance(storage_list, dict)
