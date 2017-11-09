"""Tests for policies command."""
from unittest import mock

import pytest
from click.testing import CliRunner

from lavatory.commands.policies import get_description, policies


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@mock.patch('lavatory.commands.policies.get_policy')
def test_get_description(mock_get_policy):
    description = get_description(plugin_source='test', repository='test-local')

    assert isinstance(description, dict)
    assert description['repo'] == 'test-local'
    assert 'policy_description' in description.keys()


@mock.patch('lavatory.commands.policies.get_artifactory_info')
def test_policies(mock_get_art_info, runner):
    data = {
        'test-local': {
            'repoKey': 'test-local',
            'repoType': 'LOCAL',
            'foldersCount': 473,
            'filesCount': 5915,
            'usedSpace': '105.59 GB',
            'itemsCount': 6388,
            'packageType': 'Test',
            'percentage': '8.05%'
        }
    }
    key = data.keys()
    mock_get_art_info.return_value = data, key
    result_one = runner.invoke(policies)

    assert result_one.exit_code == 0
    assert isinstance(result_one.output, str)
    assert 'test-local' in result_one.output
