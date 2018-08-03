import pytest
from unittest import mock

@pytest.fixture
def mock_party():
    with mock.patch('lavatory.utils.artifactory.load_credentials') as m:
        yield m


@pytest.fixture
def mock_credentials(mock_party):
    with mock.patch('lavatory.utils.artifactory.load_credentials') as m:
        yield m