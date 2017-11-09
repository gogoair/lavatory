"""Tests for stats command."""
from unittest import mock

import pytest
from click.testing import CliRunner

from lavatory.commands.stats import stats


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@mock.patch('lavatory.commands.stats.get_artifactory_info')
def test_command_stats(mock_artifactory, runner):
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
    mock_artifactory.return_value = data, key
    result_one = runner.invoke(stats, ['--repo', 'test-local'])
    result_two = runner.invoke(stats)

    assert result_one.exit_code == 0
    assert result_one.output == 'Done.\n'
    assert result_two.exit_code == 0
    assert result_two.output == 'Done.\n'
