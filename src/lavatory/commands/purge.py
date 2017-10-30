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
def purge(ctx, dryrun, policies_path, default):
    """Deletes artifacts based on retention policies"""
    artifactory = Artifactory()

    plugin_source = setup_pluginbase(extra_policies_path=policies_path)
    before = artifactory.list(None)
    for repo, info in before.items():
        policy_name = repo.replace("-", "_")
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
            artifactory,
            repo,
            None,
        )
        count = artifactory.purge(repo, dryrun, artifacts)
        LOG.info("Processed {}, Purged {}".format(repo, count))

    LOG.info("")
    LOG.info("Purging Performance:")
    after = artifactory.list(None)
    for repo, info in after.items():
        try:
            get_performance_report(repo, before[repo], info)
        except IndexError:
            pass

    LOG.info("Done.")
