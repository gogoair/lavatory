"""List policies and descriptions"""
import inspect
import json
import logging

import click

from ..utils.artifactory import Artifactory
from ..utils.setup_pluginbase import get_policy, setup_pluginbase

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
@click.option('--policies-path', required=False, help='Path to extra policies directory.')
@click.option(
    '--repo',
    default=None,
    multiple=True,
    required=False,
    help='Name of specific repository to run against. Can use --repo multiple times. If not provided, uses all repos.')
@click.option('--repo-type', default='local', required=False, type=click.Choice(['local', 'virtual', 'cache', 'any']),
              help="The types of repositories to search for. Local repositories by default.")
def policies(ctx, policies_path, repo, repo_type):
    """Prints out a JSON list of all repos and policy descriptions."""
<<<<<<< HEAD
    LOG.debug('Passed args: %s, %s, %s', ctx, policies_path, repo)
=======
    LOG.debug('Passed args: %s, %s, %s, %s', ctx, policies_path, repo, repo_type)
>>>>>>> added repo_type option to specify what types of repos to use. Local is default
    artifactory = Artifactory(repo_name=None)
    all_repos = artifactory.list(repo_type=repo_type)
    if repo:
        selected_repos = repo
    else:
        selected_repos = all_repos.keys()

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
