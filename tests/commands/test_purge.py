"""Unit tests for purge command"""

import pytest

from unittest import mock

from lavatory.commands.purge import apply_purge_policies, generate_purge_report

@mock.patch('lavatory.commands.purge.Artifactory')
def test_apply_purge_policies(mock_artifactory):
    """Unit test for function that applies a policy/plugin"""
    all_repos = ['yum-local', 'test_local']
    apply_purge_policies(all_repos)


@mock.patch('lavatory.commands.purge.Artifactory')
def test_purge_report(mock_artifactory):
    """Unit test for purge report"""
    mock_artifactory.list.return_value = {"yum-local": "", "test_local": ""}
    purged_repos = ['yum-local', 'test_local']
    before_data = {"yum-local": ""}
    generate_purge_report(purged_repos, before_data)
    

