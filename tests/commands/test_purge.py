"""Unit tests for purge command."""

from unittest import mock

import pytest
from click.testing import CliRunner

from lavatory.commands.purge import apply_purge_policies, generate_purge_report, purge


@mock.patch('lavatory.commands.purge.Artifactory')
def test_apply_purge_policies(mock_artifactory):
    """Unit test for function that applies a policy/plugin"""
    all_repos = ['yum-local', 'test_local']
    apply_purge = apply_purge_policies(all_repos)

    assert apply_purge is None


@mock.patch('lavatory.commands.purge.Artifactory')
def test_purge_report(mock_artifactory):
    """Unit test for purge report"""
    mock_artifactory.repos.return_value = {"yum-local": "", "test_local": ""}
    purged_repos = ['yum-local', 'test_local']
    before_data = {"yum-local": ""}
    report = generate_purge_report(purged_repos, before_data)

    assert report is None


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@mock.patch('lavatory.commands.purge.get_artifactory_info')
@mock.patch('lavatory.commands.purge.apply_purge_policies')
@mock.patch('lavatory.commands.purge.generate_purge_report')
def test_policies(mock_purge_report, mock_purge_policies, mock_get_art_info, runner):
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
    mock_purge_report.return_value = True
    mock_purge_policies.return_value = True
    result_one = runner.invoke(purge)

    assert result_one.exit_code == 0
    assert result_one.output == ''
