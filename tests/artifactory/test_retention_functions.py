"""Unit tests for testing retention functions"""

import pytest
from unittest import mock

from lavatory.utils.artifactory import Artifactory 

@pytest.fixture
@mock.patch('lavatory.utils.artifactory.load_credentials')
@mock.patch('lavatory.utils.artifactory.party.Party.request')
def artifactory(mock_party, mock_credentials):
    creds = {'artifactory_password': 'test_password',
             'artifactory_url': 'test_url',
             'artifactory_username': 'test_username'}
    mock_credentials.return_value = creds
    return Artifactory()

@mock.patch('lavatory.utils.artifactory.party.Party.find_by_aql')
def test_count_based_retention(mock_find_aql, artifactory):
    test_return = {'results': [{'name': 'test2',
                    'path': '/path/to/test/2'},
                    {'name': 'test1',
                    'path': '/path/to/test/1'}
                    ]}

    # deplicates values because of nested search at project level. Expected
    expected_return = [{'name': 'test1',
                    'path': '/path/to/test/1'},
                    {'name': 'test1',
                    'path': '/path/to/test/1'},
                    {'name': 'test2',
                    'path': '/path/to/test/2'},
                    {'name': 'test2',
                    'path': '/path/to/test/2'}
                    ]
    mock_find_aql.return_value = test_return
    purgable = artifactory.count_based_retention(retention_count=1)
    assert purgable == expected_return
    
    
