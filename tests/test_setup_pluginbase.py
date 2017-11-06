"""Unit tests for testing setting up plugin base"""

import pytest

from lavatory.exceptions import InvalidPoliciesDirectory
from lavatory.utils.setup_pluginbase import get_policy, setup_pluginbase


def test_default_policy_load():
    """tests that a default policy gets loaded in without any path"""
    plugin_source = setup_pluginbase(extra_policies_path=None)
    assert 'default' in plugin_source.list_plugins()


def test_extra_policies_path_load(tmpdir):
    """Tests that extra policies are loaded from a path"""
    temp_policy = tmpdir.join('test_policy.py')
    temp_policy.write(' ')
    plugin_source = setup_pluginbase(extra_policies_path=str(tmpdir))
    assert 'test_policy' in plugin_source.list_plugins()


def test_bad_policies_path(tmpdir):
    """Tests that an exception is raised for invalid path"""
    invalid_path = str(tmpdir) + '/bad'
    with pytest.raises(InvalidPoliciesDirectory):
        plugin_source = setup_pluginbase(extra_policies_path=invalid_path)


def test_get_default_policy():
    """tests get_policy function for default policy."""
    plugin_source = setup_pluginbase(extra_policies_path=None)
    repository = "test"
    test_policy = get_policy(plugin_source, repository)
    assert test_policy.__name__.endswith(".default")


def test_get_custom_policy(tmpdir):
    """tests get_policy function for custom policy."""
    temp_policy = tmpdir.join('test_repo.py')
    temp_policy.write(' ')
    plugin_source = setup_pluginbase(extra_policies_path=str(tmpdir))
    repository = "test-repo"
    test_policy = get_policy(plugin_source, repository)
    assert test_policy.__name__.endswith(".test_repo")
