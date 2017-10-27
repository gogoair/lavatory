"""Unit tests for testing setting up plugin base"""

import pytest

from artifactorypurge.artifactorypurge import setup_pluginbase

def test_default_policy_load():
    """tests that a default policy gets loaded in without any path"""
    plugin_source = setup_pluginbase(extra_policies_path=None)
    assert 'default' in plugin_source.list_plugins()

def test_extra_policies_path_load(tmpdir):
    """Tests that extra policies are loaded from a path"""
    temp_policy = tmpdir.join('test_policy.py')
    temp_policy.write(' ')
    plugin_source = setup_pluginbase(extra_policies_path=tmpdir)
    assert 'test_policy' in plugin_source.list_plugins()

    


