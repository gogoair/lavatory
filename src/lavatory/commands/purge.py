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
@click.option('--repo', default=None, multiple=True, required=False, 
              help='Name of specific repository to run against. Can use --repo multiple times. If not provided, uses all repos.')
def purge(ctx, dryrun, policies_path, default, repo):
    """Deletes artifacts based on retention policies"""
    artifactory = Artifactory(repo_name=None)
    plugin_source = setup_pluginbase(extra_policies_path=policies_path)

    before_repo_data = artifactory.list()
    if repo:
        all_repos = repo
    else:
        all_repos = before_repo_data.keys()
    
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
        artifacts = policy.purgelist(
            artifactory_repo
        )
        count = artifactory_repo.purge(dryrun, artifacts)
        LOG.info("Processed {}, Purged {}".format(repo, count))

    LOG.info("")
    LOG.info("Purging Performance:")
    after_repo_data = artifactory.list()
    for repo, info in after_repo_data.items():
        if repo in all_repos:
            try:
                get_performance_report(repo, before_repo_data[repo], info)
            except IndexError:
                pass

    LOG.info("Done.")
