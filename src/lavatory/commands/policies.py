"""List policies and descriptions"""
import inspect
import logging

import click 

from ..utils.artifactory import Artifactory
from ..utils.setup_pluginbase import setup_pluginbase

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
def policies(ctx, policies_path, repo):
    LOG.debug('Passed args: %s, %s, %s, %s, %s,', ctx, policies_path, repo)
    artifactory = Artifactory(repo_name=None)
    all_repos = artifactory.list()
    if repo:
        selected_repos = repo
    else:
        selected_repos = all_repos.keys()
    
    plugin_source = setup_pluginbase(extra_policies_path=policies_path)
    for repository in selected_repos:
        policy_name = repository.replace("-", "_")
        try:
            policy = plugin_source.load_plugin(policy_name)
        except ImportError:
            policy = plugin_source.load_plugin('default')
        
        click.echo("{} - {}".format(repository, inspect.getdoc(policy.purgelist)))