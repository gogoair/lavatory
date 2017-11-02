import logging

import click

from ..utils.artifactory import Artifactory
from ..utils.performance import get_performance_report
from ..utils.setup_pluginbase import setup_pluginbase

LOG = logging.getLogger(__name__)


@click.command()
@click.pass_context
@click.option('--policies-path', required=False, help='Path to extra policies directory')
@click.option(
    '--dryrun/--nodryrun', default=True, is_flag=True, help='Dryrun does not delete any artifacts. On by default')
@click.option('--default/--no-default', default=True, is_flag=True, help='If false, does not apply default policy')
@click.option(
    '--repo',
    default=None,
    multiple=True,
    required=False,
    help='Name of specific repository to run against. Can use --repo multiple times. If not provided, uses all repos.')
def purge(ctx, dryrun, policies_path, default, repo):
    """Deletes artifacts based on retention policies"""
    artifactory = Artifactory(repo_name=None)
    before_repo_data = artifactory.list()
    if repo:
        all_repos = repo
    else:
        all_repos = before_purge_data.keys()

    apply_purge_policies(all_repos, dryrun=dryrun, default=default)
    generate_purge_report(all_repos, before_purge_data)

    LOG.info("Success.")


def apply_repo_policy(all_repos, dryrun=True, default=True):
    """Sets up the plugins to find purgable artifacts and delete them. 

    Args:
        all_repos (list): List of repos to run against.
        dryrun (bool): If true, will not actually delete artifacts.
        default (bool): If true, applies default policy to repos with no specific policy.
    """
    plugin_source = setup_pluginbase(extra_policies_path=policies_path)
    LOG.info("Applying retention policies to %s", ', '.join(all_repos))
    for repo in all_repos:
        policy_name = repo.replace("-", "_")
        artifactory_repo = Artifactory(repo_name=repo)
        try:
            policy = plugin_source.load_plugin(policy_name)
        except ModuleNotFoundError:
            if default:
                LOG.info("No policy found for %s. Applying Default", repo)
                policy = plugin_source.load_plugin('default')
            else:
                LOG.info("No policy found for %s. Skipping Default", repo)
                continue
        artifacts = policy.purgelist(artifactory_repo)
        purged_count = artifactory_repo.purge(dryrun, artifacts)
        LOG.info("Processed {}, Purged {}".format(repo, purged_count))


def generate_purge_report(purged_repos, before_purge_data):
    """Generates a performance report based on deleted artifacts.

    Args:
        purged_repos (list): List of repos that had policy applied.
        before_purge_data (dict): Data on the state of Artifactory before purged artifacts
    """
    LOG.info("\nPurging Performance:")
    artifactory = Artifactory(repo_name=None)
    after_purge_data = artifactory.list()
    for repo, info in after_purge_data.items():
        if repo in purged_repos:
            try:
                get_performance_report(repo, before_purge_data[repo], info)
            except IndexError:
                pass
