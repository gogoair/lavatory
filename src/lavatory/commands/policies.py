"""List policies and descriptions"""
import inspect
import json
import logging

import click

from ..consts import REPO_TYPES
from ..utils.get_artifactory_info import get_artifactory_info
from ..utils.setup_pluginbase import get_policy, setup_pluginbase

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
@click.option('--policies-path', required=False, help='Path to extra policies directory.', show_default=True)
@click.option(
    '--repo',
    default=None,
    multiple=True,
    required=False,
    show_default=True,
    help='Name of specific repository to run against. Can use --repo multiple times. If not provided, uses all repos.')
@click.option(
    '--repo-type',
    default='local',
    required=False,
    type=click.Choice(REPO_TYPES),
    show_default=True,
    help="The types of repositories to search for.")
def policies(ctx, policies_path, repo, repo_type):
    """Prints out a JSON list of all repos and policy descriptions."""
    LOG.debug('Passed args: %s, %s, %s, %s', ctx, policies_path, repo, repo_type)

    storage_info, selected_repos = get_artifactory_info(repo_names=repo, repo_type=repo_type)

    plugin_source = setup_pluginbase(extra_policies_path=policies_path)
    policy_list = [get_description(plugin_source, r) for r in selected_repos]
    click.echo(json.dumps(policy_list))


def get_description(plugin_source, repository):
    """Given a repository and plugin source, gets policy description.

    Args:
        plugin_source (PluginBase): The source of plugins from PluginBase.
        repository (str): The name fo the repository to get policy description.
    
    Returns:
        dict: A dictionary of repo name and policy description
    """
    policy = get_policy(plugin_source, repository)
    policy_desc = inspect.getdoc(policy.purgelist)
    policy_dict = {"repo": repository, "policy_description": policy_desc}
    LOG.info("%s - %s", repository, policy_desc)
    return policy_dict
