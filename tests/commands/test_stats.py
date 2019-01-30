"""Tests for stats command."""
from unittest import mock

import pytest
from click.testing import CliRunner

from lavatory.commands.stats import stats


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@mock.patch('lavatory.commands.stats.get_storage')
@mock.patch('lavatory.commands.stats.get_repos')
def test_command_stats(mock_get_repos, mock_get_storage, runner):
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
    mock_get_repos.return_value = data
    mock_get_storage.return_value = {}
    result_one = runner.invoke(stats, ['--repo', 'test-local'])
    result_two = runner.invoke(stats)

    assert result_one.exit_code == 0
    assert result_two.exit_code == 0
