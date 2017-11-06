"""List policies and descriptions"""
import inspect
import json
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
    """Prints out a JSON list of all repos and policy descriptions."""
    LOG.debug('Passed args: %s, %s, %s, %s, %s,', ctx, policies_path, repo)
    artifactory = Artifactory(repo_name=None)
    all_repos = artifactory.list()
    if repo:
        selected_repos = repo
    else:
        selected_repos = all_repos.keys()
    
    plugin_source = setup_pluginbase(extra_policies_path=policies_path)
    policy_list = []
    for repository in selected_repos:
        policy_name = repository.replace("-", "_")
        try:
            policy = plugin_source.load_plugin(policy_name)
        except ImportError:
            policy = plugin_source.load_plugin('default')
        policy_disc = inspect.getdoc(policy.purgelist)    
        policy_list.append({"repo": repository, "policy": policy_disc})
        LOG.info("{} - {}".format(repository, policy_disc))
    
    click.echo(json.dumps(policy_list))